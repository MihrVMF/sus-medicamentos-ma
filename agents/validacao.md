# Agente de validação

Roda depois de uma carga, na branch `lucas`. Não altera `main`.

Confere, e abre issue se falhar:

- O volume não despenca sem explicação contra a carga anterior.
- `AP_CMP` não vem vazio. A análise usa a competência de atendimento, não o mês do arquivo.
- Abril de 2023 não tem arquivo próprio no DATASUS. Os atendimentos desse mês aparecem no arquivo de junho de 2023.
- Entre junho e agosto de 2023 a queda de APACs fica na faixa de 18% a 38% descrita no README. Fora dessa faixa, sinaliza em vez de corrigir o número.
- Não inventa dado para tampar buraco.
