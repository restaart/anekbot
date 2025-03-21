import openai

from app.config import settings

client = openai.AsyncClient(api_key=settings.openai_token)


async def get_embedding(text: str | list[str]) -> list[list[float]] | list[float]:
    response = await client.embeddings.create(
        input=text,
        model=settings.embedding_model,
        dimensions=settings.embedding_vector_size,
    )

    if isinstance(text, str):
        return response.data[0].embedding

    return [embedding.embedding for embedding in response.data]
