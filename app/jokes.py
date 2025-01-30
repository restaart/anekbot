import asyncio
from typing import List, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Joke
from app.database import async_session
from app.ai import get_embedding, get_photo_description


class JokeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_similar_jokes(
        self, 
        text: str, 
        limit: int = 5,
        min_likes: int = 0
    ) -> List[Tuple[Joke, float]]:
        """
        Find most similar jokes by embedding distance
        
        Args:
            text: Text to find similar jokes for
            limit: Maximum number of jokes to return
            min_likes: Minimum number of likes required
            
        Returns:
            List of tuples containing (joke, distance)
        """
        # Get embedding for input text
        embedding = await get_embedding(text)
        
        # Query for closest jokes by L2 distance
        query = (
            select(Joke, Joke.embedding.l2_distance(embedding).label("distance"))
            .where(Joke.likes_count >= min_likes)
            .order_by("distance")
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        return [(joke, float(distance)) for joke, distance in result]



if __name__ == "__main__":
    async def main():
        """Example usage of JokeRepository"""
        async with async_session() as session:
            repo = JokeRepository(session)

            # Example: find similar jokes to a query
            query_text = "Программист заходит в бар"
            similar_jokes = await repo.get_similar_jokes(
                text=query_text,
                limit=3,
                min_likes=5
            )

            print(f"\nQuery: {query_text}")
            print("\nSimilar jokes:")
            for joke, distance in similar_jokes:
                print(f"\nDistance: {distance:.3f}")
                print(f"Likes: {joke.likes_count}")
                print(f"Text: {joke.text}")

    asyncio.run(main())

