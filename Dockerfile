FROM python:3.12-alpine as builder
RUN pip install --no-cache-dir --upgrade poetry==1.8.5

WORKDIR /app
COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.in-project true

RUN poetry install --no-dev --no-root

FROM python:3.12-alpine
RUN adduser -D appuser
USER appuser

WORKDIR /app

COPY --from=builder /app/.venv ./.venv

COPY --chown=appuser:appuser . .

ENV PATH="/app/.venv/bin:$PATH" \
    VIRTUAL_ENV="/app/.venv" \
    PYTHONPATH="/app/.venv/lib/python3.12/site-packages"

ENTRYPOINT ["./scripts/entrypoint.sh"]