import asyncio
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from fastapi import BackgroundTasks, FastAPI, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from scraper import REGIOES_DISPONIVEIS, executar_varredura

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(BASE_DIR / ".playwright-browsers"))

app = FastAPI(title="Varredouro de Leads")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

jobs: Dict[str, Dict] = {}


def executar_async(coro):
    if sys.platform.startswith("win"):
        loop = asyncio.ProactorEventLoop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    return asyncio.run(coro)


def atualizar_job(job_id: str, patch: Dict) -> None:
    jobs[job_id].update(patch)
    jobs[job_id]["updated_at"] = datetime.now().isoformat(timespec="seconds")


def progress_factory(job_id: str):
    def progress(event: Dict) -> None:
        job = jobs[job_id]
        if event.get("type") == "message":
            atualizar_job(job_id, {"message": event.get("message", "")})
        elif event.get("type") == "total":
            atualizar_job(
                job_id,
                {
                    "total": event.get("total", 0),
                    "message": event.get("message", ""),
                },
            )
        elif event.get("type") == "item_done":
            atual = job.get("processed", 0) + 1
            total = max(1, job.get("total", 0))
            atualizar_job(
                job_id,
                {
                    "processed": atual,
                    "progress": min(100, round((atual / total) * 100)),
                    "message": f"Extraindo lojas: {atual}/{job.get('total', 0)}",
                },
            )

    return progress


def executar_job(job_id: str, regioes: List[str], max_lojas: int, abrir_navegador: bool) -> None:
    try:
        atualizar_job(job_id, {"status": "running", "message": "Iniciando varredura..."})
        job_dir = OUTPUTS_DIR / job_id
        resultado = executar_async(
            executar_varredura(
                regioes=regioes,
                max_lojas=max_lojas,
                output_dir=job_dir,
                headless=not abrir_navegador,
                progress_cb=progress_factory(job_id),
            )
        )

        resumo = resultado["resumo"]
        duplicadas = resultado.get("duplicadas_ignoradas", 0)
        historico_total = resultado.get("historico_total", resumo["total"])
        mensagem_final = "Varredura finalizada. Baixe o Excel ou CSV abaixo."
        if duplicadas:
            mensagem_final = f"Varredura finalizada. {duplicadas} lojas repetidas foram ignoradas. Baixe os novos leads abaixo."
        atualizar_job(
            job_id,
            {
                "status": "done",
                "progress": 100,
                "processed": resumo["total"],
                "message": mensagem_final,
                "summary": resumo,
                "excel_path": resultado["excel_path"],
                "csv_path": resultado["csv_path"],
                "log_path": resultado.get("log_path", ""),
                "duplicadas_ignoradas": duplicadas,
                "historico_total": historico_total,
            },
        )
    except Exception as e:
        detalhe = str(e).strip() or repr(e)
        atualizar_job(
            job_id,
            {
                "status": "error",
                "message": f"Erro na execucao: {detalhe}",
            },
        )


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "regioes": REGIOES_DISPONIVEIS},
    )


@app.post("/executar")
def executar(
    background_tasks: BackgroundTasks,
    regioes: List[str] = Form(...),
    max_lojas: int = Form(20),
    abrir_navegador: bool = Form(False),
):
    regioes_validas = [r for r in regioes if r in REGIOES_DISPONIVEIS]
    if not regioes_validas:
        regioes_validas = REGIOES_DISPONIVEIS

    max_lojas = max(1, min(int(max_lojas), 100))
    job_id = uuid.uuid4().hex[:12]
    jobs[job_id] = {
        "id": job_id,
        "status": "queued",
        "progress": 0,
        "processed": 0,
        "total": 0,
        "message": "Na fila para execucao...",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "regioes": regioes_validas,
        "max_lojas": max_lojas,
    }

    background_tasks.add_task(executar_job, job_id, regioes_validas, max_lojas, abrir_navegador)
    return RedirectResponse(url=f"/status/{job_id}", status_code=303)


@app.get("/status/{job_id}", response_class=HTMLResponse)
def status_page(request: Request, job_id: str):
    job = jobs.get(job_id)
    if not job:
        return templates.TemplateResponse("not_found.html", {"request": request}, status_code=404)
    return templates.TemplateResponse("status.html", {"request": request, "job": job})


@app.get("/api/jobs/{job_id}")
def status_api(job_id: str):
    job = jobs.get(job_id)
    if not job:
        return JSONResponse({"error": "Job nao encontrado"}, status_code=404)
    return dict(job)


def arquivo_do_job(job_id: str, tipo: str) -> Path:
    job = jobs.get(job_id)
    if not job:
        raise FileNotFoundError("Job nao encontrado")
    key = "excel_path" if tipo == "excel" else "csv_path"
    path = Path(job.get(key, ""))
    if not path.exists():
        raise FileNotFoundError("Arquivo nao encontrado")
    return path


@app.get("/download/{job_id}/{tipo}")
def download(job_id: str, tipo: str):
    if tipo not in {"excel", "csv"}:
        return JSONResponse({"error": "Tipo invalido"}, status_code=400)
    try:
        path = arquivo_do_job(job_id, tipo)
        return FileResponse(path, filename=path.name)
    except FileNotFoundError as e:
        return JSONResponse({"error": str(e)}, status_code=404)
