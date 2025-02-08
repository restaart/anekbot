import datetime

import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai import get_embedding
from app.jokes import JokeRepository
from app.models import Joke


@pytest.fixture
async def jokes_test_data(db_session: AsyncSession):
    jokes = [
        Joke(
            external_id="1",
            text="A robot walks into a bar",
            comments_count=10,
            likes_count=1000,
            embedding=await get_embedding("A robot walks into a bar"),
            date=datetime.datetime(2024, 1, 1),
        ),
        Joke(
            external_id="2",
            text="A zebra walks into a bar",
            comments_count=20,
            likes_count=2000,
            embedding=await get_embedding("A zebra walks into a bar"),
            date=datetime.datetime(2024, 1, 1),
        ),
        Joke(
            external_id="3",
            text="The Moon is made of cheese",
            comments_count=20,
            likes_count=3000,
            embedding=await get_embedding("The Moon is made of cheese"),
            date=datetime.datetime(2024, 1, 1),
        ),
    ]

    for joke in jokes:
        db_session.add(joke)
    await db_session.commit()

    yield

    await db_session.execute(delete(Joke))
    await db_session.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query,expected_external_id",
    [("I was in a zoo yesterday", "2"), ("I like astronomy", "3")],
)
async def test_get_top_n_similar_jokes(
    db_session, jokes_test_data, query, expected_external_id
):
    repo = JokeRepository(db_session)
    similar_jokes = await repo.get_top_n_similar_jokes(query=query)
    assert similar_jokes[0][0].external_id == expected_external_id


@pytest.mark.asyncio
@pytest.mark.parametrize("min_likes,expected_count", [(2500, 1), (3500, 0)])
async def test_get_top_n_similar_jokes_with_likes_filtering(
    db_session, jokes_test_data, min_likes, expected_count
):
    repo = JokeRepository(db_session)

    similar_jokes = await repo.get_top_n_similar_jokes(
        query="I was in a zoo yesterday", min_likes=min_likes
    )

    assert len(similar_jokes) == expected_count
