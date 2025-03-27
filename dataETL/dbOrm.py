from dataETL.dataModel import Base

def create_tables(engine):
    # makes table based on data Model
    Base.metadata.create_all(engine)