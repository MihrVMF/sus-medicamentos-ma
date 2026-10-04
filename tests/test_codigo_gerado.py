"""Trava erros comuns de código gerado por IA neste pipeline."""

import re
from pathlib import Path

import pipeline.extrair_carregar as mod

RAIZ = Path(__file__).resolve().parents[1]
FONTE = (RAIZ / "pipeline" / "extrair_carregar.py").read_text()


def test_fonte_nao_tem_segredo():
    proibido = re.compile(
        r"(api[_-]?key\s*=\s*['\"]|ghp_|github_pat_|AIza|BEGIN PRIVATE KEY|"
        r"private_key|client_email|ya29\.)",
        re.I,
    )
    assert proibido.search(FONTE) is None


def test_carga_nao_usa_credencial_no_codigo():
    assert "to_gbq" in FONTE
    assert "service_account" not in FONTE
    assert ".json" not in FONTE


def test_ftp_anonimo_sem_senha():
    assert "ftp.login()" in FONTE
    assert "ftp.login(" not in FONTE.replace("ftp.login()", "")


def test_periodo_do_readme_bate_com_o_codigo():
    readme = (RAIZ / "README.md").read_text()
    assert "jan/2022" in readme and "jun/2026" in readme
    assert mod.INICIO == (2022, 1)
    assert mod.FIM == (2026, 6)
    assert mod.UF == "MA"


def test_tabela_e_projeto_nao_estao_vazios():
    assert mod.PROJETO.strip()
    assert "." in mod.TABELA
    assert mod.FTP_HOST == "ftp.datasus.gov.br"
