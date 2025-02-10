# Anekbot

A Telegram bot, that make jokes, that are related(sometimes) to your messages.
## Features

- Semantic joke search using AI embeddings
- Database storage for jokes with metadata
- Configurable similarity matching
- Async API design
- Docker support for easy deployment


## Installation
Edit `docker-compose-full.yml`, adding your bot token, OpenAI API key, etc and then:
```bash
docker compose -f "docker-compose-full.yml" up --build
```

### Running Tests

```bash
poetry run pytest
```

