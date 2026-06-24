# Varredouro de Leads - Site local

Interface web para buscar lojas de moveis por regiao em Sao Paulo e gerar arquivos CSV/Excel para download.

## 1. Instalar dependencias

Abra o terminal dentro da pasta do projeto e rode:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

No Linux/Mac, a ativacao do ambiente e:

```bash
source .venv/bin/activate
```

## 2. Rodar o site

```bash
uvicorn app:app --reload
```

Depois abra:

```text
http://127.0.0.1:8000
```

No Windows, tambem da para abrir com dois cliques no arquivo `run.bat`.

## 3. Como usar

1. Escolha a quantidade de lojas por regiao.
2. Marque as regioes desejadas.
3. Clique em **Iniciar varredura**.
4. Aguarde a tela de status finalizar.
5. Baixe o resultado em Excel ou CSV.

## Observacoes importantes

- Para teste, use 2 a 5 lojas por regiao.
- O Google Maps pode exibir captcha ou bloquear scraping se muitas buscas forem feitas.
- Para producao real e estabilidade maior, o ideal e migrar a coleta para uma API oficial, como Google Places API.
- Use os dados coletados respeitando LGPD e boas praticas de contato comercial.
