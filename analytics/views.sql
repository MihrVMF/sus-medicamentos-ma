-- Camada analytics sobre raw.apac_medicamentos.
-- Colunas do arquivo disseminado de APAC (DBF), usadas pelo script:
-- AP_CMP (competência do atendimento, AAAAMM), AP_PRIPAL (procedimento principal,
-- no CEAF é o código do medicamento na SIGTAP), AP_MUNPCN (município do paciente),
-- AP_UFMUN (município do estabelecimento), AP_VL_AP (valor), AP_CIDPRI.
-- arquivo_origem e data_carga são acrescentados na carga.
-- Abril/2023 não tem arquivo próprio; a competência continua em AP_CMP.

CREATE SCHEMA IF NOT EXISTS `sus-medicamentos-ma.analytics`;

CREATE OR REPLACE VIEW `sus-medicamentos-ma.analytics.apac_mensal` AS
SELECT
  AP_CMP AS competencia,
  COUNT(*) AS apacs,
  COUNT(DISTINCT NULLIF(AP_MUNPCN, '')) AS municipios_paciente,
  SUM(SAFE_CAST(AP_VL_AP AS FLOAT64)) AS valor_total
FROM `sus-medicamentos-ma.raw.apac_medicamentos`
WHERE AP_CMP IS NOT NULL AND AP_CMP != ''
GROUP BY competencia;

CREATE OR REPLACE VIEW `sus-medicamentos-ma.analytics.apac_medicamento` AS
SELECT
  AP_CMP AS competencia,
  AP_PRIPAL AS medicamento,
  COUNT(*) AS apacs,
  SUM(SAFE_CAST(AP_VL_AP AS FLOAT64)) AS valor_total
FROM `sus-medicamentos-ma.raw.apac_medicamentos`
WHERE AP_CMP IS NOT NULL AND AP_CMP != ''
GROUP BY competencia, medicamento;

CREATE OR REPLACE VIEW `sus-medicamentos-ma.analytics.apac_municipio` AS
SELECT
  AP_CMP AS competencia,
  AP_MUNPCN AS municipio_paciente,
  COUNT(*) AS apacs
FROM `sus-medicamentos-ma.raw.apac_medicamentos`
WHERE AP_CMP IS NOT NULL AND AP_CMP != ''
GROUP BY competencia, municipio_paciente;
