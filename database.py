import aiosqlite

class Database:
    async def startapp(self):
        async with aiosqlite.connect('database.db') as db:
            await db.execute("CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, age INTEGER, city TEXT, country TEXT, bio TEXT);")
            await db.execute(
                "CREATE TABLE IF NOT EXISTS travels (id TEXT, name TEXT, bio TEXT);")
            await db.execute(
                "CREATE TABLE IF NOT EXISTS members (id TEXT, username TEXT);")
            await db.execute(
                "CREATE TABLE IF NOT EXISTS writes (id TEXT, for TEXT, text TEXT, file TEXT);")
            await db.execute(
                "CREATE TABLE IF NOT EXISTS locations (id TEXT, locate TEXT, fromtime TEXT, totime TEXT);")
            await db.commit()

    async def getuser(self, username):
        async with aiosqlite.connect('database.db') as db:
            async with db.execute(f"SELECT * FROM users WHERE username='{username}';") as cursor:
                async for row in cursor:
                    return row
        return False

    async def create_user(self, username, age, city, country, bio):
        async with aiosqlite.connect('database.db') as db:
            #await db.execute(f"INSERT INTO users (username, age, city, country, bio) VALUES (‘{username}’, {age}, '{city}','{country}','{bio}');")
            #await db.execute(f"IF EXISTS (SELECT * FROM users WHERE username='{username}') UPDATE users SET age={age}, city='{city}', country='{country}', bio='{bio}' WHERE username='{username}') ELSE INSERT INTO users (username, age, city, country, bio) VALUES (‘{username}’, {age}, '{city}','{country}','{bio}');")
            await db.execute(f"INSERT INTO users (username, age, city, country, bio) VALUES ('{username}', {age}, '{city}','{country}','{bio}') ON CONFLICT(username) DO UPDATE SET age={age}, city='{city}', country='{country}', bio='{bio}';")
            await db.commit()

    async def isuniquetravelname(self, name):
        async with aiosqlite.connect('database.db') as db:
            async with db.execute(f"SELECT * FROM travels WHERE name='{name}';") as cursor:
                async for row in cursor:
                    if row: return False
        return True

    async def addfriendintravel(self, id, username):
        async with aiosqlite.connect('database.db') as db:
            await db.execute(f"INSERT INTO members (id, username) VALUES ('{id}', '{username}');")
            await db.commit()
    async def create_travel(self, id, name, bio, username):
        async with aiosqlite.connect('database.db') as db:
            await db.execute(f"INSERT INTO travels (id, name, bio) VALUES ('{id}', '{name}', '{bio}');")
            await db.commit()
        await self.addfriendintravel(id, username)

    async def create_location(self, id, locate, fromtime, totime):
        async with aiosqlite.connect('database.db') as db:
            await db.execute(f"INSERT INTO locations (id, locate, fromtime, totime) VALUES ('{id}', '{locate}', '{fromtime}','{totime}');")
            await db.commit()

    async def watch_my_travels(self, username):
        def cov(s):
            return "'" + s + "'"
        async with aiosqlite.connect('database.db') as db:
            async with db.execute(f"SELECT id FROM members WHERE username='{username}';") as cursor:
                lst = list(map(lambda x:x[0], await cursor.fetchall()))
                lst = ','.join(map(cov, lst))
            async with db.execute(f"SELECT * FROM travels WHERE id IN ({lst});") as cursor:
                return await cursor.fetchall()

    async def get_travel(self, uid):
        travel = {}
        async with aiosqlite.connect('database.db') as db:
            async with db.execute(f"SELECT * FROM travels WHERE id='{uid}';") as cursor:
                travel['about'] = await cursor.fetchone()
            async with db.execute(f"SELECT * FROM locations WHERE id='{uid}';") as cursor:
                travel['locations'] = await cursor.fetchall()
            async with db.execute(f"SELECT username FROM members WHERE id='{uid}';") as cursor:
                travel['members'] = await cursor.fetchall()
        return travel

    async def deletetravel(self, uid):
        async with aiosqlite.connect('database.db') as db:
            await db.execute(f"DELETE FROM travels WHERE id='{uid}';")
            await db.execute(f"DELETE FROM locations WHERE id='{uid}';")
            await db.execute(f"DELETE FROM writes WHERE id='{uid}';")
            await db.execute(f"DELETE FROM members WHERE id='{uid}';")
            await db.commit()

    async def updatetravelbio(self, uid, bio):
        async with aiosqlite.connect('database.db') as db:
            await db.execute(f"UPDATE travels SET bio='{bio}' WHERE id='{uid}';")
            await db.commit()

    async def getnotes(self, uid, username):
        async with aiosqlite.connect('database.db') as db:
            async with db.execute(f"SELECT * FROM notes WHERE id='{uid}' AND for IN ('All','{username}');") as cursor:
                return await cursor.fetchall()

    async def addnote(self, uid, forr, text, filename):
        async with aiosqlite.connect('database.db') as db:
            await db.execute(f"INSERT INTO notes (id, for, text, file) VALUES ('{uid}', '{forr}', '{text}','{filename}');")
            await db.commit()

    async def ratelocks(self):
        async with aiosqlite.connect('database.db') as db:
            async with db.execute(f"SELECT locate,COUNT(*) as count FROM locations GROUP BY locate ORDER BY count DESC;") as cursor:
                return await cursor.fetchall()

    async def ratetravelers(self):
        async with aiosqlite.connect('database.db') as db:
            async with db.execute(f"SELECT username,COUNT(*) as count FROM members GROUP BY username ORDER BY count DESC;") as cursor:
                return await cursor.fetchall()

