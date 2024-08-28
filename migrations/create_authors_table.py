from migrations.migration import Migration


class CreateAuthorsTable(Migration):
    async def up(self):
        # Create table if not exists
        await self.conn.execute('''
                CREATE TABLE IF NOT EXISTS authors (
                    id BIGINT PRIMARY KEY,
                    gender_id INT,
                    age INT,
                    preferred_speech_styles int[]
                );
            ''')
        print("Table 'authors' is ready.")

    async def down(self):
        await self.conn.execute('''
               DROP TABLE IF EXISTS authors;
           ''')
        print("Table 'authors' has been dropped if it existed.")
