import asyncio

import asyncpg

import config
from migrations.create_authors_table import CreateAuthorsTable


async def create_migration_table(conn):
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS migrations (
            name TEXT PRIMARY KEY,
            applied_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
        )
    """)


async def check_migration_applied(conn, name):
    return await conn.fetchval("""
        SELECT 1 FROM migrations WHERE name = $1
    """, name)


async def record_migration(conn, name):
    await conn.execute("""
        INSERT INTO migrations (name) VALUES ($1)
    """, name)


async def main():
    conn = await asyncpg.connect(config.DATABASE_URL)
    await create_migration_table(conn)

    migrations = [
        CreateAuthorsTable(conn)
    ]

    for migration in migrations:
        migration_name = type(migration).__name__
        if not await check_migration_applied(conn, migration_name):
            await migration.down()
            await migration.up()
            await record_migration(conn, migration_name)

    await conn.close()


if __name__ == '__main__':
    asyncio.run(main())
