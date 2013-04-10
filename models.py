from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float


engine = create_engine('sqlite:///stats.db', echo=True)
Base = declarative_base()


class Log(Base):
    __table__ = "logs"
    id = Column(Integer, primary_key=True)
    access_time = Column(DateTime)
    publisher_time = Column(Float)
    traverse_time = Column(Float)
    commit_time = Column(Float)
    transform_time = Column(Float)
    setstate_time = Column(Float)
    total_object_loads = Column(Integer)
    object_loads_from_cache = Column(Integer)
    objects_modified = Column(Integer)
    action = Column(String)
    url = Column(String)
    start_RSS = Column(Float)
    end_RSS = Column(Float)
