import os
from sqlalchemy import create_engine
from dataETL.dbOrm import create_tables
from dataETL.populateDb import populate_db
from dataETL.dataModel import Base

engine = create_engine(f"sqlite:///./{os.environ["DB_NAME"]}", echo=True)
Base.metadata.drop_all(engine)
create_tables(engine)
populate_db(engine)
# create_relations(engine)