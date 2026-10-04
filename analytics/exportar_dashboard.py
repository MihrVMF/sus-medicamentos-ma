"""Exporta analytics.apac_mensal para dashboard/mensal.json.

Usa a credencial local do Google Cloud, via pandas-gbq. Não grava segredo.
"""

import json
from pathlib import Path

import pandas_gbq

CONSULTA = """
SELECT competencia, apacs, municipios_paciente, valor_total
FROM `sus-medicamentos-ma.analytics.apac_mensal`
ORDER BY competencia
"""


def main():
    df = pandas_gbq.read_gbq(CONSULTA, project_id="sus-medicamentos-ma")
    destino = Path(__file__).resolve().parents[1] / "dashboard" / "mensal.json"
    linhas = json.loads(df.to_json(orient="records"))
    destino.write_text(json.dumps(linhas, ensure_ascii=False, indent=2))
    print(f"{len(linhas)} competências em {destino}")


if __name__ == "__main__":
    main()
