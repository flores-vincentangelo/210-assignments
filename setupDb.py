import os
from sqlalchemy import MetaData, Table, create_engine
from dataETL.dbOrm import create_db_create_tables
from dataETL.populateDb import populate_db
from dataETL.dataModel import DataModel

metadata_obj = MetaData()
engine = create_engine(f"sqlite:///./{os.environ["DB_NAME"]}", echo=True)

data = Table(
    "data",
    metadata_obj
)

data.drop(engine, checkfirst=True)
create_db_create_tables(engine)
populate_db(engine)