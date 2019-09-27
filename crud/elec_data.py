from databases import Database
from sqlalchemy.orm import Session
from datetime import datetime
from crud.decorator import con_warpper, query2sql
from db.db_config import session_make
from db_model import ElecData


@con_warpper
async def get_latest(conn: Database, shard_id: int, session: Session = session_make(engine=None)):
    model = ElecData.model(point_id=shard_id)
    query = session. \
        query(model). \
        order_by(model.id.desc()). \
        limit(1)
    return await conn.fetch_one(query2sql(query))


@con_warpper
async def get_by_id(conn: Database, shard_id: int, data_id: int, session: Session = session_make(engine=None)):
    model = ElecData.model(point_id=shard_id)
    query = session. \
        query(model). \
        filter(model.id == data_id)
    return await conn.fetch_one(query2sql(query))

@con_warpper
async def get_multi(conn:Database,shard_id:int,time_before:datetime,time_after:datetime,session : Session = session_make(engine=None)):
    model = ElecData.model(point_id=shard_id)
    query = session. \
        query(model.id,model.time). \
        filter(model.time.between(str(time_before),str(time_after))). \
        order_by(model.id)
    return await conn.fetch_all(query2sql(query))