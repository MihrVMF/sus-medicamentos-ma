# SUS Medicamentos MA

Pipeline de dados públicos do SUS: dispensação de medicamentos do Componente
Especializado da Assistência Farmacêutica (CEAF) no Maranhão, de 2022 a 2026.

## Arquitetura

DATASUS (FTP, arquivos .dbc) → Python → BigQuery (raw → analytics) → Power BI

## Fonte

- Sistema: SIA/SUS, APAC de Medicamentos (arquivos `AMMAaamm.dbc`)
- Período: jan/2022 a jun/2026
- Volume: 1.350.154 registros em 53 arquivos mensais

## Como executar

    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    python pipeline/extrair_carregar.py

## Achados da validação dos dados

- O arquivo de abril/2023 não foi publicado pelo DATASUS; os atendimentos
  desse mês aparecem no arquivo de junho/2023
- Toda análise temporal usa a competência de atendimento (`AP_CMP`), não o
  mês do arquivo
- Queda real de 18% a 38% no número de APACs entre junho e agosto de 2023

## Qualidade e segurança

Repositório público de propósito, para mostrar o trabalho. O CI no GitHub Actions roda em todo push e pull request:

- testes com pytest e cobertura de código (96% no pipeline, mínimo de 70% para o build passar)
- lint com ruff
- detecção de segredos com gitleaks, que falha o build se encontrar credencial

O `.gitignore` deixa de fora credenciais (`.env`, chave privada, JSON de service account) e artefatos de cobertura. Nenhum segredo fica no código. A carga no BigQuery usa a credencial local de quem executa, não uma chave versionada.
