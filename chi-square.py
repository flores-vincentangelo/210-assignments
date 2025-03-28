import json
import os
from sqlalchemy import create_engine, func, inspect, select, text
from sqlalchemy.orm import Session
from dataETL.dataModel import Respondents

engine = create_engine(f"sqlite:///./{os.environ["DB_NAME"]}", echo=True)


def get_attr_values(engine):
    categorical_attributes_list = [
        "gender",
        "relationship_status",
        "employment_status",
        "monthly_income",
        "pet_ownership",
        "housing_type",
        "primary_cook",
        "preferred_dining",
        "health_consciousness",
        "frequency_eating_out",
        "frequency_takeout_delivery",
        "frequency_cook_home",
        "frequency_grocery",
]
    categorical_dict_counts = {}
    mapper = inspect(Respondents)
    for column in mapper.attrs:
        if column.key not in categorical_attributes_list:
            continue
        
        categorical_dict_counts[column.key] = {}
        with Session(engine) as session:
            group_by = select(column, func.count(column).label("counts")).group_by(column)
            for result_tuple in session.execute(group_by):
                categorical_dict_counts[column.key][result_tuple[0]] = {
                    "total": result_tuple[1]
                } 
                print(result_tuple)
    return categorical_dict_counts

def chi_square(engine, att1, att2):
    chi_square_dict = {}
    with Session(engine) as session:
        for value1 in att1:
            chi_square_dict[value1] = {}
            for value2 in att2:
                chi_square_dict[value1][value2] = 0
                sqlText = text(f"select count(*) from Respondents where gender = \"{value1}\" AND relationship_status = \"{value2}\"")
                for count in session.scalars(sqlText):
                    chi_square_dict[value1][value2] = count
                    print(f"gender = {value1} and relationship_status = {value2}: {count}")
    print(chi_square_dict)

categorical_dict_counts = get_attr_values(engine)
with open("categorical_attr.json", "w") as f:
    f.write(json.dumps(categorical_dict_counts))