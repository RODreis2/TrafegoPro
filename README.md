# TrafegoPro

The first microservice in the project, organized to study hexagonal
architecture.

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

## Responsibilities

```text
domain      -> business rules and entities
application -> use cases and contracts required by the application
adapters    -> technical input and output: HTTP, database, queues, external APIs
```

## Expected Flow

```text
controller inbound
  -> use case
    -> port
      -> repository outbound
```
