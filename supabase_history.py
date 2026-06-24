import os
from typing import Dict, Iterable, List


CAMPOS_DB = [
    "regiao",
    "nome",
    "telefone",
    "whatsapp",
    "endereco",
    "categoria",
    "horario",
    "site",
    "nota",
    "url",
]


def database_url() -> str:
    return os.getenv("SUPABASE_DB_URL", "").strip()


def supabase_ativo() -> bool:
    return bool(database_url())


def conectar():
    import psycopg

    return psycopg.connect(database_url())


def carregar_lojas() -> List[Dict]:
    if not supabase_ativo():
        return []

    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select regiao, nome, telefone, whatsapp, endereco, categoria,
                       horario, site, nota, url
                from lojas_coletadas
                order by created_at asc
                """
            )
            rows = cur.fetchall()

    return [dict(zip(CAMPOS_DB, row)) for row in rows]


def salvar_lojas(lojas: Iterable[Dict]) -> None:
    if not supabase_ativo():
        return

    with conectar() as conn:
        with conn.cursor() as cur:
            for loja in lojas:
                cur.execute(
                    """
                    insert into lojas_coletadas (
                        regiao, nome, telefone, whatsapp, endereco, categoria,
                        horario, site, nota, url
                    )
                    values (
                        %(regiao)s, %(nome)s, %(telefone)s, %(whatsapp)s,
                        %(endereco)s, %(categoria)s, %(horario)s, %(site)s,
                        %(nota)s, %(url)s
                    )
                    on conflict do nothing
                    """,
                    {campo: loja.get(campo, "") for campo in CAMPOS_DB},
                )
        conn.commit()
