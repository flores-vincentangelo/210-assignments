import json
import os
from sqlalchemy import create_engine, func, inspect, select, text
from sqlalchemy.orm import Session
from dataETL.dataModel import Respondents
import numpy as np
from scipy.stats import chi2_contingency

engine = create_engine(f"sqlite:///./{os.environ["DB_NAME"]}", echo=False)

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

def prepare_attr_mapping(engine, categorical_attributes_list):

    categorical_attr_mappings = {}
    column_attr_list = []
    column_attr_values_dict = {}
    mapper = inspect(Respondents)
    for column_attr in mapper.attrs:
        if column_attr.key not in categorical_attributes_list:
            continue
        column_attr_list.append(column_attr.key)
        column_attr_values_dict[column_attr.key] = []
        with Session(engine) as session:
            group_by = select(column_attr, func.count(column_attr).label("counts")).group_by(column_attr)
            for result_tuple in session.execute(group_by):
                column_attr_values_dict[column_attr.key].append(result_tuple[0])
                # categorical_attr_mappings[column_attr.key][result_tuple[0]] = {
                #     "total": result_tuple[1]
                # } 
    
    for attr1 in column_attr_list:
        categorical_attr_mappings[attr1] = {}
        for attr2 in column_attr_list:
            if attr1 == attr2:
                continue
            categorical_attr_mappings[attr1][attr2] = {}
            for value1 in column_attr_values_dict[attr1]:
                categorical_attr_mappings[attr1][attr2][value1] = {}
                for value2 in column_attr_values_dict[attr2]:
                    categorical_attr_mappings[attr1][attr2][value1][value2] = 0
    return categorical_attr_mappings

def get_other_totals(engine, categorical_attributes_list):
    
    mapper = inspect(Respondents)
    filepath = "categorical_attr_mappings.txt"
    if os.path.exists(filepath):
        os.remove(filepath)
    with open(filepath, "a") as f:
        for column_attr in mapper.attrs:
            for column_attr2 in mapper.attrs:
                if column_attr.key not in categorical_attributes_list or column_attr2.key not in categorical_attributes_list:
                    continue
                
                if column_attr.key == column_attr2.key:
                    continue

                group_by = select(column_attr, column_attr2, func.count(column_attr).label("count")).group_by(column_attr).group_by(column_attr2)
                with Session(engine) as session:
                    for result_tuple in session.execute(group_by):
                        # if ((column_attr.key == "gender" and column_attr2.key == "relationship_status") or (column_attr.key == "relationship_status" and column_attr2.key == "gender")):
                        x = f"{column_attr.key} {column_attr2.key} {result_tuple}"
                        print(x)
                        f.write(f"{x}\n")


categorical_attr_mappings = prepare_attr_mapping(engine, categorical_attributes_list)
with open("categorical_attr.json", "w") as f:
    f.write(json.dumps(categorical_attr_mappings))
get_other_totals(engine, categorical_attributes_list, categorical_attr_mappings)

def chi_square(array):
    critical_value_dict = {
        1: 3.841,
        2: 5.991,
        3: 7.815,
        4: 9.488,
        5: 11.070
    }

    obs = np.array([[7, 6 ],[1,0], [17, 19]])
    res = chi2_contingency(obs, correction=False)
    res.statistic
    res.pvalue
    res.dof
    res.expected_freq
    if res.statistic > critical_value_dict[res.dof]:
        print("reject null hypothesis")
    else:
        print("accept null hypothesis")
    print("done")

chi_square([])