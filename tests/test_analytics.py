from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def test_views_usam_competencia_e_nao_tem_segredo():
    sql = (RAIZ / "analytics" / "views.sql").read_text()
    assert "AP_CMP" in sql
    assert "AP_PRIPAL" in sql
    assert "AP_MUNPCN" in sql
    assert "raw.apac_medicamentos" in sql
    assert "PRIVATE KEY" not in sql
    assert "service_account" not in sql


def test_dashboard_nao_inventa_numero():
    html = (RAIZ / "dashboard" / "index.html").read_text()
    assert "mensal.json" in html
    assert "1.350.154" not in html
