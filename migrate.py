import asyncio
import os
import pickle

# import asyncpg
# from pgvector.asyncpg import register_vector


def load_embeddings():
    EMBEDDINGS_PATH = 'data/embeddings'
    embedings = []
    files = sorted(os.listdir(EMBEDDINGS_PATH), key=lambda x:int(x.split('_')[1]))
    for file in files:
        path = EMBEDDINGS_PATH + "/" + file
        with open(path, 'rb') as f:
            batch = pickle.load(f)
            embedings.extend(batch)

    return embedings

def load_data(return_values = True):
    df = pandas.read_csv('data/baneks.csv')
    df.date = pandas.to_datetime(df.date, unit='s')
    df = df.rename(columns={'date':'cdate', 'text':'body'})
    df = df[:-1]
    df['embedding'] = load_embeddings()
    df.embedding = df.embedding.apply(np.array)
    df = df['cdate likes_count body embedding'.split()]

    if return_values:
        return df.values
    return df

# def load_data():
#     with open('data/init.pkl', 'rb') as f:
#         return pickle.load(f)


# async def migrate(pg_url):
#     conn = await asyncpg.connect(pg_url)
#     await conn.execute('CREATE EXTENSION IF NOT EXISTS vector;')
#     await register_vector(conn)
#     # Execute a statement to create a new table.
#     await conn.execute('''
#         CREATE TABLE IF NOT EXISTS aneks(
#             id serial PRIMARY KEY,
#             cdate timestamp,
#             likes_count int,
#             body text,
#             embedding vector(1536)
#         );
#     ''')
#
#     # await conn.execute('CREATE INDEX ON aneks USING ivfflat (embedding vector_ip_ops);')
#
#     data = load_data()
#
#     await conn.executemany('''
#         INSERT INTO aneks(cdate, likes_count, body, embedding)
#         VALUES($1, $2, $3, $4);
#     ''', data)


# if __name__ == '__main__':
#     pg_url = os.environ.get('PG_DSN', 'postgresql://postgres:password@localhost/postgres')
#     asyncio.run(migrate(pg_url))
