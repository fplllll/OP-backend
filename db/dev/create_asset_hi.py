from db_model import Asset
from db import session_make, meta_engine

from sqlalchemy.ext.declarative import declarative_base
from db_model.asset_hi import AssetHI
import datetime
import random

session = session_make(meta_engine)
x = session.query(Asset.id).filter(Asset.asset_type == 0).all()

base = declarative_base()
for row in x:
    model = AssetHI.model(point_id=row.id, base=base)  # registe to metadata for all pump_unit

from sqlalchemy import create_engine

META_URL = 'mysql://git:Fpl8315814.@123.56.7.137/op_meta?charset=utf8'
engine = create_engine(META_URL, encoding='utf-8',
                       pool_pre_ping=True)
base.metadata.create_all(engine)

for row in x:
    initial_datetime = datetime.datetime(2016, 1, 1, 0, 0, 0, 0)
    tmp = []
    model = AssetHI.model(point_id=row.id)  # registe to metadata for all pump_unit
    for i in range(1, 900):
        r = model(id=i, time=str(initial_datetime), health_indicator=80 + random.random() * 10)
        initial_datetime += datetime.timedelta(days=1)
        tmp.append(r)
    session.add_all(tmp)
    session.commit()