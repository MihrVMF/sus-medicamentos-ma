# Agente de código

Cuida de `pipeline/extrair_carregar.py` na branch `lucas`. Nunca commita em `main` e não abre pull request.

Quando for chamado:

- Tira do código o que é configuração: projeto, tabela, UF, período, host FTP e pasta local. Lê de variável de ambiente, com os valores atuais como padrão.
- A carga não pode fazer `replace` na tabela final. Grava numa tabela de staging e só troca se o mês inteiro carregou.
- O FTP precisa de timeout e de nova tentativa. Se o download quebrar, apaga o `.part` e sobe o erro.
- Troca `print` por log. Aviso de coluna extra ou faltando continua visível.
- Não coloca credencial, caminho de JSON nem segredo no código. A carga segue na credencial local de quem executa.
- Roda `pytest` antes de commitar. Se a cobertura cair de 70%, não commita.
