import asyncio
import pickle

from app.ai import get_embedding


async def main():
    messages = [
        "A robot walks into a bar",
        "A zebra walks into a bar",
        "The Moon is made of cheese",
        "I was in a zoo yesterday",
        "I like astronomy",
    ]

    try:
        with open("precomputed_embeddings.pkl", "rb") as f:
            precomputed_emb = pickle.load(f)
    except FileNotFoundError:
        precomputed_emb = {}

    messages = [m for m in messages if m not in precomputed_emb]

    if not messages:
        print(f"No new embeddings created.")
        return

    emb = await get_embedding(messages)

    print(f"Created {len(emb)} new embeddings")

    precomputed_emb = precomputed_emb | dict(zip(messages, emb))

    with open("precomputed_embeddings.pkl", "wb") as f:
        pickle.dump(precomputed_emb, f)


if __name__ == "__main__":
    asyncio.run(main())
