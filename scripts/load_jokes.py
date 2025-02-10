import asyncio
import csv
import logging
import sys
from datetime import datetime
from itertools import batched
from typing import List, Dict

from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError

from app.ai import get_embedding
from app.database import get_session
from app.models import Joke

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BATCH_SIZE = 500


def create_joke(row: Dict, embedding) -> Joke:
    """Create a joke instance from row .data"""
    row = map_file_row(row)
    return Joke(**row, embedding=embedding)


def map_file_row(row: Dict) -> Dict:
    """Map CSV row to database schema"""
    return {
        "external_id": row["external_id"],
        "text": row["text"],
        "likes_count": int(row["likes_count"]),
        "has_my_like": row["has_my_like"] == "1",
        "date": datetime.fromtimestamp(int(row["date"])),
    }


async def process_batch(session, batch: List[Dict]) -> int:
    """Process a batch of jokes and return number of added jokes"""
    jokes_to_add = []

    for row in batch:
        exists = await session.execute(
            select(Joke).where(Joke.external_id == row["external_id"])
        )
        if exists.scalar_one_or_none():
            continue

        jokes_to_add.append(row)

    if not jokes_to_add:
        return 0

    texts = [j["text"] for j in jokes_to_add]
    embeddings = await get_embedding(texts)
    jokes = [create_joke(j, e) for j, e in zip(jokes_to_add, embeddings)]

    try:
        session.add_all(jokes)
        await session.commit()
        return len(jokes)
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Database error: {e}")
        raise


async def load_jokes_from_csv(filepath: str):
    """Load jokes from CSV file into database with batching"""

    async with get_session() as session:
        with open(filepath, "r", encoding="utf-8") as f:
            for batch in batched(csv.DictReader(f), BATCH_SIZE):
                added = await process_batch(session, batch)
                logger.info(f"Processed {len(batch)} jokes, added {added} new jokes")
        logger.info(f"Reindexing...")
        await session.execute(text('SET maintenance_work_mem = "128MB";'))
        await session.execute(text("REINDEX INDEX jokes_embedding_idx;"))
        logger.info(f"Done.")


def main():
    try:
        path = sys.argv[1]
    except KeyError as e:
        raise Exception("File Path arg is missing.") from e
    asyncio.run(load_jokes_from_csv(path))


if __name__ == "__main__":
    main()
