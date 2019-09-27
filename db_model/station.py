from sqlalchemy import Column, Integer
from sqlalchemy import String, Text
from sqlalchemy.orm import relationship

from db import Base, table_args


class Station(Base):
    __tablename__ = 'station'
    __table_args__ = table_args

    STATIONS =  {1: 'HuHeHaoTe', 2: 'ErTuoKeQi', 3: 'BaoTou'}

    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True)
    location = Column(String(32), nullable=True)
    memo = Column(Text, nullable=True)
    telephone = Column(String(30), nullable=True)

    sharding_db_id = Column(Integer, nullable=False)  # 指向该站数据库id

    assets = relationship('Asset', back_populates='station')
    measure_points = relationship('MeasurePoint', back_populates="station")
