from pathlib import Path

from scraper import HISTORICO_ARQUIVO, carregar_csv_lojas, parece_loja_de_moveis
from supabase_history import salvar_lojas, supabase_ativo


def main() -> None:
    if not supabase_ativo():
        raise SystemExit("Defina SUPABASE_DB_URL antes de migrar o historico.")

    path = Path("outputs") / HISTORICO_ARQUIVO
    lojas = [loja for loja in carregar_csv_lojas(path) if parece_loja_de_moveis(loja)]
    salvar_lojas(lojas)
    print(f"{len(lojas)} lojas enviadas para o Supabase.")


if __name__ == "__main__":
    main()
