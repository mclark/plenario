import os
from sqlalchemy import Column, Integer, String, Boolean, Table, types
from sqlalchemy.dialects.postgresql import TIMESTAMP, DOUBLE_PRECISION
from geoalchemy2 import Geometry
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

from wopr.database import Base, engine

#MetaTable = Table('meta_master', Base.metadata,
#    autoload=True, autoload_with=engine)

MasterTable = Table('dat_master', Base.metadata,
    autoload=True, autoload_with=engine)

class NullInteger(types.TypeDecorator):
    impl = types.Integer
    def process_result_value(self, value, engine):
        try:
            return int(value)
        except ValueError:
            return None

def crime_table(name, metadata):
    table = Table(name, metadata,
            Column('id', Integer),
            Column('case_number', String(length=10)),
            Column('date', TIMESTAMP),
            Column('block', String(length=50)),
            Column('iucr', String(length=10)),
            Column('primary_type', String(length=100)),
            Column('description', String(length=100)),
            Column('location_description', String(length=50)),
            Column('arrest', Boolean),
            Column('domestic', Boolean),
            Column('beat', String(length=10)),
            Column('district', String(length=5)),
            Column('ward', NullInteger),
            Column('community_area', String(length=10)),
            Column('fbi_code', String(length=10)),
            Column('x_coordinate', NullInteger, nullable=True),
            Column('y_coordinate', NullInteger, nullable=True),
            Column('year', NullInteger),
            Column('updated_on', TIMESTAMP, default=None),
            Column('latitude', DOUBLE_PRECISION(precision=53)),
            Column('longitude', DOUBLE_PRECISION(precision=53)),
            Column('location', String(length=50)),
    extend_existing=True)
    return table
