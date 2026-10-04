"""Testes do pipeline sem FTP real e sem BigQuery."""

from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd

import pipeline.extrair_carregar as mod


def test_listar_meses_um_unico_mes():
    assert mod.listar_meses((2024, 6), (2024, 6)) == [(2024, 6)]


def test_listar_meses_vira_o_ano():
    assert mod.listar_meses((2022, 11), (2023, 2)) == [
        (2022, 11),
        (2022, 12),
        (2023, 1),
        (2023, 2),
    ]


def test_nome_arquivo_padrao_datasus():
    assert mod.nome_arquivo(2026, 1) == "AMMA2601.dbc"
    assert mod.nome_arquivo(2022, 12) == "AMMA2212.dbc"


def test_baixar_pula_ausente_reusa_local_e_baixa_novo(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "PASTA", tmp_path)
    (tmp_path / "AMMA2201.dbc").write_bytes(b"ja-existe")

    def retr(cmd, callback):
        callback(b"conteudo-dbc")

    ftp = MagicMock()
    ftp.nlst.return_value = ["AMMA2201.dbc", "AMMA2202.dbc"]
    ftp.retrbinary.side_effect = retr
    monkeypatch.setattr(mod, "FTP", lambda host: ftp)

    saida = mod.baixar_todos(["AMMA2299.dbc", "AMMA2201.dbc", "AMMA2202.dbc"])

    assert [p.name for p in saida] == ["AMMA2201.dbc", "AMMA2202.dbc"]
    assert (tmp_path / "AMMA2201.dbc").read_bytes() == b"ja-existe"
    assert (tmp_path / "AMMA2202.dbc").read_bytes() == b"conteudo-dbc"
    assert not (tmp_path / "AMMA2202.dbc.part").exists()
    ftp.quit.assert_called_once()


def test_ler_dbc_converte_e_devolve_texto(tmp_path, monkeypatch):
    dbc = tmp_path / "AMMA2306.dbc"
    dbc.write_bytes(b"dbc")

    def fake_dbc2dbf(origem, destino):
        Path(destino).write_bytes(b"dbf")

    class Tabela:
        def __init__(self, caminho, encoding=None):
            assert encoding == "latin-1"
            self._linhas = [{"AP_CMP": "202304", "QT": "2"}]

        def __iter__(self):
            return iter(self._linhas)

    monkeypatch.setattr(mod, "dbc2dbf", fake_dbc2dbf)
    monkeypatch.setattr(mod, "DBF", Tabela)

    df = mod.ler_dbc(dbc)

    assert (tmp_path / "AMMA2306.dbf").exists()
    assert df["AP_CMP"].iloc[0] == "202304"
    assert str(df["QT"].dtype) == "string"


def test_main_replace_no_primeiro_e_append_nos_demais(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "PASTA", tmp_path)
    monkeypatch.setattr(mod, "INICIO", (2024, 1))
    monkeypatch.setattr(mod, "FIM", (2024, 2))

    def baixar(nomes):
        caminhos = []
        for nome in nomes:
            caminho = tmp_path / nome
            caminho.write_bytes(b"x")
            caminhos.append(caminho)
        return caminhos

    frames = {
        "AMMA2402.dbc": pd.DataFrame({"A": ["1"], "B": ["2"]}).astype("string"),
        "AMMA2401.dbc": pd.DataFrame({"A": ["3"], "C": ["9"]}).astype("string"),
    }
    chamadas = []

    def to_gbq(df, **kwargs):
        chamadas.append(
            {
                "if_exists": kwargs["if_exists"],
                "colunas": list(df.columns),
                "linhas": len(df),
                "projeto": kwargs["project_id"],
                "tabela": kwargs["destination_table"],
            }
        )

    monkeypatch.setattr(mod, "baixar_todos", baixar)
    monkeypatch.setattr(mod, "ler_dbc", lambda caminho: frames[caminho.name].copy())
    monkeypatch.setattr(mod.pandas_gbq, "to_gbq", to_gbq)

    mod.main()

    assert [c["if_exists"] for c in chamadas] == ["replace", "append"]
    assert chamadas[0]["colunas"][:2] == ["A", "B"]
    assert "C" not in chamadas[1]["colunas"]
    assert "B" in chamadas[1]["colunas"]
    assert chamadas[1]["colunas"][-2:] == ["arquivo_origem", "data_carga"]
    assert chamadas[0]["projeto"] == "sus-medicamentos-ma"
    assert chamadas[0]["tabela"] == "raw.apac_medicamentos"
