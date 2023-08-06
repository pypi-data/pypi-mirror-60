from phlasch.db.tables import link


async def create_link(conn, address):
    insert = link.insert().values(address=address)
    cursor = await conn.execute(insert)
    row = await cursor.fetchone()
    return dict(row) if row else None


async def list_links(conn):
    select = link.select()
    cursor = await conn.execute(select)
    rows = await cursor.fetchall()
    return [dict(row) for row in rows] if rows else []


async def retrieve_link(conn, shortcut):
    select = link.select().where(link.c.shortcut == shortcut)
    cursor = await conn.execute(select)
    row = await cursor.fetchone()
    return dict(row) if row else None


async def update_link_shortcut(conn, pk, shortcut):
    update = link.update().values(
        shortcut=shortcut,
    ).where(link.c.id == pk)
    await conn.execute(update)


async def update_link_visits(conn, pk):
    update = link.update().values(
        visits=link.c.visits + 1,
    ).where(link.c.id == pk)
    await conn.execute(update)
