"""Exporta analytics.apac_mensal para dashboard/mensal.json.

Usa a credencial local do Google Cloud. Não grava segredo.
"""

import json
from pathlib import Path

from google.cloud import bigquery

CONSULTA = """
SELECT competencia, apacs, municipios_paciente, valor_total
FROM `sus-medicamentos-ma.analytics.apac_mensal`
ORDER BY competencia
"""


def main():
    cliente = bigquery.Client(project="sus-medicamentos-ma")
    linhas = [dict(linha) for linha in cliente.query(CONSULTA).result()]
    destino = Path(__file__).resolve().parents[1] / "dashboard" / "mensal.json"
    destino.write_text(json.dumps(linhas, ensure_ascii=False, default=str, indent=2))
    print(f"{len(linhas)} competências em {destino}")


if __name__ == "__main__":
    main()
