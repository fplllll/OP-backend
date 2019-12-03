import random

from databases import Database
from sqlalchemy.orm import Session

from crud.base import con_warpper, query2sql
from custom_lib.treelib import Tree
from db.db_config import session_make
from db_model import Asset
from db_model.organization import Station, BranchCompany, RegionCompany


@con_warpper
async def get_multi(
        conn: Database, skip: int, limit: int, session: Session = session_make(engine=None)
):
    query = session.query(Station).order_by(
        Station.id).offset(skip).limit(limit)
    return await conn.fetch_all(query2sql(query))


@con_warpper
async def get(conn: Database, id: int, session: Session = session_make(engine=None)):
    query = session.query(Station).filter(Station.id == id)

    return await conn.fetch_one(query2sql(query))


@con_warpper
async def get_tree(conn: Database, session: Session = session_make(engine=None)):
    assets = await conn.fetch_all(
        query2sql(session.query(Asset.id, Asset.name, Asset.station_id.label('parent_id')).filter(
            Asset.asset_level == 0
        )))
    stations = await conn.fetch_all(
        query2sql(session.query(Station.id, Station.name, Station.bc_id.label('parent_id'))))
    bcs = await conn.fetch_all(
        query2sql(session.query(BranchCompany.id, BranchCompany.name, BranchCompany.rc_id.label('parent_id'))))
    rcs = await conn.fetch_all(query2sql(session.query(RegionCompany.id, RegionCompany.name)))

    tree = Tree()
    tree.create_node(tag="root", identifier="root")

    color = ["#2D5F73",  "#538EA6", "#F2D1B3", "#F2B8A2", "#F28C8C"]

    def item_maker(item, parent_type, self_type):
        temp = dict(item)
        if parent_type:
            temp['parent_id'] = parent_type + str(temp['parent_id'])
        if self_type == 'asset':
            temp['value'] = 1
        temp['id'] = self_type + str(temp['id'])
        temp["itemStyle"] = {"color": random.choice(color)}
        return temp

    assets = [item_maker(row, 'st', 'asset') for row in assets]
    stations = [item_maker(row, 'bc', 'st') for row in stations]
    bcs = [item_maker(row, 'rc', 'bc') for row in bcs]
    rcs = [item_maker(row, None, 'rc') for row in rcs]

    for item in rcs + bcs + stations + assets:
        tree.create_node(
            data=item,
            identifier=item['id'],
            parent=item['parent_id'] if 'parent_id' in item else 'root',
        )

    return tree.to_dict(with_data=True)["children"]


@con_warpper
async def get_bc(
        conn: Database, skip: int, limit: int, session: Session = session_make(engine=None)
):
    query = (
        session.query(BranchCompany)
        .order_by(BranchCompany.id)
        .offset(skip)
        .limit(limit)
    )
    return await conn.fetch_all(query2sql(query))


@con_warpper
async def get_rc(
        conn: Database, skip: int, limit: int, session: Session = session_make(engine=None)
):
    query = (
        session.query(RegionCompany)
        .order_by(RegionCompany.id)
        .offset(skip)
        .limit(limit)
    )
    return await conn.fetch_all(query2sql(query))
