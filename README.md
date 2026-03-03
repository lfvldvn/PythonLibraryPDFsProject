# libraryPDFs

## Variaveis de ambiente

- `SECRET_KEY`: chave secreta usada para sessao Flask.
- `ADMIN_PASSWORD_HASH` (recomendado): hash da senha admin gerado com `werkzeug.security.generate_password_hash`.
- `ADMIN_PASSWORD` (alternativa): senha em texto puro para hash em runtime (evite em producao).
