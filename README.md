# SUS Medicamentos MA

[![CI](https://github.com/MihrVMF/sus-medicamentos-ma/actions/workflows/ci.yml/badge.svg?branch=lucas)](https://github.com/MihrVMF/sus-medicamentos-ma/actions/workflows/ci.yml)
[![coverage](https://img.shields.io/badge/coverage-98%25-2ea44f)](https://github.com/MihrVMF/sus-medicamentos-ma/blob/lucas/pyproject.toml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3120/)
[![MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Pipeline de dados públicos do SUS: dispensação de medicamentos do Componente
Especializado da Assistência Farmacêutica (CEAF) no Maranhão, de jan/2022 a jun/2026.

O trabalho novo fica na branch `lucas`. `main` é a linha do repositório original.

## Arquitetura

DATASUS (FTP, arquivos .dbc) → Python → BigQuery (`raw`) → analytics → Power BI

O script `pipeline/extrair_carregar.py` faz três stages. Analytics e Power BI ainda não estão no repositório.

| Stage | O que faz |
| --- | --- |
| Extrair | Baixa do FTP do DATASUS os arquivos `AMMAaamm.dbc` que ainda não estão em `dados/brutos`. Se o download quebra, apaga o arquivo parcial. |
| Transformar | Converte `.dbc` em `.dbf`, lê em latin-1 e deixa todas as colunas como texto. O mês mais novo define o layout. Mês antigo é alinhado a esse layout. |
| Carregar | Grava em `sus-medicamentos-ma.raw.apac_medicamentos`, região US. O primeiro arquivo faz replace. Os seguintes fazem append. |

## Fonte

- Sistema: SIA/SUS, APAC de Medicamentos (arquivos `AMMAaamm.dbc`)
- Período: jan/2022 a jun/2026
- Volume: 1.350.154 registros em 53 arquivos mensais

## Como executar

A carga usa a credencial local do Google Cloud de quem executa. Nenhuma chave fica no repositório.

macOS e Linux:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python pipeline/extrair_carregar.py

Windows (PowerShell):

    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    python pipeline/extrair_carregar.py

Testes, na mesma venv, com as dependências de `requirements-dev.txt`:

    pip install -r requirements-dev.txt
    pytest

## CI

O workflow `.github/workflows/ci.yml` roda no GitHub Actions, em runner `ubuntu-latest`, a cada push e pull request. Os três jobs rodam em paralelo. Nenhum deles baixa o DATASUS nem grava no BigQuery.

| Job | O que faz | Falha quando |
| --- | --- | --- |
| test | Instala as dependências e roda pytest com cobertura | Um teste quebra, ou a cobertura do pipeline fica abaixo de 70% |
| lint | Roda ruff em `pipeline` e `tests` | O ruff aponta erro de estilo ou de correção |
| secrets | Roda gitleaks no histórico do git | Encontra credencial, token ou chave |

## Achados da validação dos dados

- O arquivo de abril/2023 não foi publicado pelo DATASUS. Os atendimentos desse mês aparecem no arquivo de junho/2023.
- Toda análise temporal usa a competência de atendimento (`AP_CMP`), não o mês do arquivo.
- Queda real de 18% a 38% no número de APACs entre junho e agosto de 2023.

## Qualidade e segurança

Repositório público de propósito, para mostrar o trabalho. A cobertura medida no pipeline é 98%. O build exige no mínimo 70%.

O `.gitignore` deixa de fora `.env`, chave privada, JSON de service account, a pasta `dados/` e artefatos de cobertura. A licença é MIT.
