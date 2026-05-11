# TrafegoPro

TrafegoPro e um MVP de planejamento de rotas para coletas, entregas e paradas
operacionais. A aplicacao recebe um ponto inicial, uma lista de paradas e um
destino final, calcula uma ordem otimizada para visitar os pontos e exibe o
resultado em um mapa interativo.

O projeto foi construido como uma demonstracao tecnica de backend, frontend
simples e organizacao em arquitetura hexagonal. A proposta nao e substituir um
TMS ou roteirizador profissional, mas mostrar uma base clara para evoluir um
produto de logistica urbana.

## O que o projeto faz

- Busca enderecos usando Nominatim/OpenStreetMap.
- Otimiza a ordem das paradas com calculo local de distancia entre coordenadas.
- Mostra a rota em um mapa com tiles do OpenStreetMap.
- Usa o servidor publico de demonstracao do OSRM para desenhar a geometria da
  rota pelas ruas no frontend.
- Diferencia tipos de parada: coleta, entrega e parada generica.
- Valida coordenadas, labels, tipos de parada e tamanho maximo da rota com
  Pydantic.
- Retorna erros controlados quando o provedor externo de geocoding falha.
- Inclui headers basicos de seguranca na resposta HTTP.

## Stack

- Python 3.12+
- FastAPI
- Pydantic
- Uvicorn
- Leaflet
- OpenStreetMap / Nominatim
- OSRM demo server
- Pytest
- uv

## Arquitetura

O codigo segue uma organizacao inspirada em arquitetura hexagonal:

```text
src/
  domain/       -> entidades, value objects e regras de dominio
  application/  -> casos de uso, DTOs, mappers, portas e servicos
  adapters/     -> controllers HTTP e integracoes externas
static/         -> interface web com mapa
```

Fluxo principal:

```text
HTTP controller
  -> caso de uso
    -> servico de aplicacao
      -> entidades e value objects de dominio
```

Essa separacao deixa o otimizador de rotas independente do FastAPI e facilita a
troca de adaptadores externos, como geocoding ou persistencia futura.

## Como rodar

Requisitos:

- Python 3.12+
- uv instalado

Instale/sincronize as dependencias e suba a API:

```bash
uv run uvicorn main:app --reload
```

Acesse a interface:

```text
http://127.0.0.1:8000
```

Documentacao interativa da API:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

### Otimizar rota

```text
POST /routes/optimize
```

Exemplo de payload:

```json
{
  "start": {
    "label": "Inicio",
    "latitude": -23.55052,
    "longitude": -46.63331
  },
  "stops": [
    {
      "label": "Coleta A",
      "type": "pickup",
      "latitude": -23.56168,
      "longitude": -46.65598
    },
    {
      "label": "Entrega B",
      "type": "dropoff",
      "latitude": -23.54894,
      "longitude": -46.63882
    }
  ],
  "destination": {
    "label": "Destino",
    "latitude": -23.58741,
    "longitude": -46.65763
  }
}
```

Estrategias atuais:

```text
ate 8 paradas intermediarias -> brute force, testa todas as ordens possiveis
9 paradas intermediarias     -> nearest neighbor, escolhe a proxima mais perto
```

O backend otimiza usando distancia em linha reta entre coordenadas. No mapa, o
frontend tenta buscar uma geometria de ruas no OSRM apenas para melhorar a
visualizacao da linha.

### Geocoding

```text
POST /geocode
```

```json
{
  "address": "Av. Paulista, 1000, Sao Paulo, SP"
}
```

Resposta:

```json
{
  "address": "Av. Paulista, 1000, Sao Paulo, SP",
  "latitude": -23.564,
  "longitude": -46.652,
  "provider": "nominatim",
  "display_name": "..."
}
```

### Sugestoes de endereco

```text
GET /geocode/search?q=paulista&limit=5
```

Esse endpoint alimenta o autocomplete da interface web.

## Testes e checagens

Rode a suite automatizada:

```bash
uv run pytest
```

Cheque sintaxe/imports:

```bash
uv run python -m compileall main.py src
```

## Estado atual e limites conhecidos

- Nao ha login, autenticacao, cadastro de usuario ou banco de dados neste MVP.
- Nao ha API keys ou secrets obrigatorios para rodar localmente.
- O Nominatim publico deve ser usado com baixo volume. Em producao, o projeto
  precisaria de cache, rate limiting e configuracao dedicada de provedor.
- O OSRM usado no frontend e o servidor publico de demonstracao; ele nao deve
  ser tratado como infraestrutura de producao.
- A otimizacao usa distancia geodesica, nao tempo real de transito, janela de
  entrega, capacidade de veiculo ou restricoes comerciais.
- Uma versao publica deveria adicionar observabilidade, CORS especifico do
  ambiente, rate limiting e provedores externos configuraveis.

## Sobre a classe User

O projeto chegou a ter um esqueleto de `User`, mas ele nao estava conectado a
nenhum endpoint, nao tinha fluxo de login e ainda carregava um campo de senha
sem politica de hash. Esse codigo foi removido para manter o escopo coerente:
TrafegoPro, nesta versao, e um planejador de rotas sem autenticacao.

Se autenticacao entrar no roadmap, ela deve voltar como uma feature completa:
modelo de usuario, hash de senha, persistencia, endpoints, testes e politica de
sessao ou token.
