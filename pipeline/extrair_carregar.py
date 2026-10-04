"""
Pipeline: APAC de Medicamentos (SIA/SUS) do Maranhão
Extrai os arquivos mensais do FTP do DATASUS e carrega no BigQuery (dataset raw).
"""

from datetime import datetime, timezone
from ftplib import FTP
from pathlib import Path

import pandas as pd
import pandas_gbq
from dbfread import DBF
from pyreaddbc import dbc2dbf

# ---------------- Configuração ----------------
PROJETO = "sus-medicamentos-ma"
TABELA = "raw.apac_medicamentos"
UF = "MA"
INICIO = (2022, 1)   # (ano, mês)
FIM = (2026, 6)

FTP_HOST = "ftp.datasus.gov.br"
FTP_PASTA = "/dissemin/publicos/SIASUS/200801_/Dados"
PASTA = Path("dados/brutos")


# ---------------- Funções ----------------
def listar_meses(inicio, fim):
    """Gera a lista de (ano, mês) entre inicio e fim, inclusive."""
    ano, mes = inicio
    meses = []
    while (ano, mes) <= fim:
        meses.append((ano, mes))
        mes += 1
        if mes == 13:
            ano, mes = ano + 1, 1
    return meses


def nome_arquivo(ano, mes):
    """Monta o nome do arquivo no padrão do DATASUS. Ex.: AMMA2601.dbc"""
    return f"AM{UF}{ano % 100:02d}{mes:02d}.dbc"


def baixar_todos(nomes):
    """Etapa E: baixa do FTP os arquivos que ainda não estão na pasta local."""
    ftp = FTP(FTP_HOST)
    ftp.login()
    ftp.cwd(FTP_PASTA)
    disponiveis = set(ftp.nlst())

    baixados = []
    try:
        baixados.extend(_baixar_lista(ftp, disponiveis, nomes))
    finally:
        ftp.quit()
    return baixados


def _baixar_lista(ftp, disponiveis, nomes):
    baixados = []
    for nome in nomes:
        destino = PASTA / nome
        if nome not in disponiveis:
            print(f"[AVISO] {nome} não existe no FTP, pulando")
            continue
        if not destino.exists():
            temporario = destino.with_name(destino.name + ".part")
            try:
                with open(temporario, "wb") as f:
                    ftp.retrbinary(f"RETR {nome}", f.write)
                temporario.replace(destino)
            except Exception:
                temporario.unlink(missing_ok=True)
                raise
            print(f"Baixado: {nome}")
        baixados.append(destino)
    return baixados


def ler_dbc(caminho_dbc):
    """Etapa T: descompacta .dbc -> .dbf e devolve um DataFrame só com texto."""
    caminho_dbf = caminho_dbc.with_suffix(".dbf")
    if not caminho_dbf.exists():
        temporario = caminho_dbf.with_name(caminho_dbf.name + ".part")
        dbc2dbf(str(caminho_dbc), str(temporario))
        temporario.replace(caminho_dbf)
    tabela = DBF(caminho_dbf, encoding="latin-1")
    return pd.DataFrame(iter(tabela)).astype("string")


def main():
    PASTA.mkdir(parents=True, exist_ok=True)

    # Do mais recente para o mais antigo: o layout mais novo vira a referência
    meses = listar_meses(INICIO, FIM)[::-1]
    nomes = [nome_arquivo(ano, mes) for ano, mes in meses]
    print(f"{len(nomes)} meses no recorte")

    arquivos = baixar_todos(nomes)

    # Etapa L: carga no BigQuery, um mês por vez
    data_carga = datetime.now(timezone.utc)
    colunas_ref = None
    total = 0

    for caminho in arquivos:
        df = ler_dbc(caminho)

        if colunas_ref is None:
            colunas_ref = list(df.columns)
        else:
            extras = set(df.columns) - set(colunas_ref)
            faltando = set(colunas_ref) - set(df.columns)
            if extras or faltando:
                print(f"[AVISO] {caminho.name}: extras={extras} faltando={faltando}")
            df = df.reindex(columns=colunas_ref).astype("string")

        df["arquivo_origem"] = caminho.name
        df["data_carga"] = data_carga

        primeira = total == 0
        pandas_gbq.to_gbq(
            df,
            destination_table=TABELA,
            project_id=PROJETO,
            location="US",
            if_exists="replace" if primeira else "append",
            progress_bar=False,
        )
        total += len(df)
        print(f"{caminho.name}: {len(df):>7,} linhas | acumulado: {total:>9,}")

    print(f"\nConcluído: {total:,} linhas em {PROJETO}.{TABELA}")


if __name__ == "__main__":
    main()