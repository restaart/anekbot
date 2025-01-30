import logging
from time import sleep

import openai

from app.config import settings

client = openai.AsyncClient(api_key=settings.OPENAI_TOKEN)


async def get_embedding(text: str | list[str]) -> list[list[float]] | list[float]:
    response = await client.embeddings.create(input=text, model=settings.EMBEDDING_MODEL)

    if isinstance(text, str):
        return response.data[0].embedding

    return [embedding.embedding for embedding in response.data]



def get_photo_description(url: str) -> str:
    logging.info(f"AI: Describing photo: {url}")
    prompt = "Ответь одним предложением, без вводных слов и повторения вопроса. Опиши фото без деталей."
    return client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": url,
                        },
                    },
                ],
            }
        ],
        max_tokens=300,
        temperature=0.
    ).choices[0].message.content
