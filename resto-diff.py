import os
from difflib import SequenceMatcher
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from dataETL.dataModel import Respondents


# print(SequenceMatcher(None, "Andoks", "Biggs").ratio())

engine = create_engine(f"sqlite:///./{os.environ["DB_NAME"]}", echo=True)

def simillar(string_a, string_b):
    return SequenceMatcher(None, string_a, string_b).ratio()


def query(engine):
    with Session(engine) as session:
        query = select(Respondents.favorite_restaurants)
        for result in session.execute(query):
            

# query(engine)
simillar("kfc", "kfc")