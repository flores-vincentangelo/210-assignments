import os

from sqlalchemy import create_engine
from dataModel import Base

engine = create_engine(f"sqlite:///./{os.environ["DB_NAME"]}", echo=True)

Base.metadata.create_all(engine)