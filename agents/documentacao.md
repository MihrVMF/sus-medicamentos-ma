# Agente de documentação

Mantém o README alinhado com o código, na branch `lucas`. Não altera `main` e não abre pull request.

Quando o período, o comando de execução ou os jobs do CI mudarem:

- Atualiza o período no README para bater com `INICIO` e `FIM`.
- Deixa o comando de execução para macOS e para Windows, não só PowerShell.
- Lista o que cada job do CI faz: test, lint e secrets.
- Não descreve badge, cobertura ou licença que não exista no repositório.
- Não coloca e-mail, telefone, chave ou nome de arquivo de credencial no README.
