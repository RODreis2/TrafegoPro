# TrafegoPro

Primeiro microsservico do projeto, organizado para estudar arquitetura
hexagonal.

```text
src/
  domain/
    entities/
      user.py

  application/
    ports/
      user_repository.py
    use_cases/
      create_user.py
      get_user.py

  adapters/
    inbound/
      controllers/
    outbound/
      repositories/
        postgres_user_repository.py
```

## Responsabilidades

```text
domain      -> regras e entidades de negocio
application -> casos de uso e contratos que a aplicacao precisa
adapters    -> entrada e saida tecnica: HTTP, banco, filas, APIs externas
```

## Fluxo esperado

```text
controller inbound
  -> use case
    -> port
      -> repository outbound
```
