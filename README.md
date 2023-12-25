# ShortAI

## Run locally

### Create .env file. 
```bash
cp .env.example .env
```

### Docker-compose

To run all services:
``` bash
docker compose up -d --build
```

``` bash
docker compose ps
```

``` bash
docker compose logs -f
```

# Control psql
``` bash
docker compose run db bash

>>> psql postgres://
```
