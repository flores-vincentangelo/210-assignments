import os
from sqlalchemy import create_engine, select, text, func, inspect
from sqlalchemy.orm import Session
from dataETL.dataModel import Respondents
from scipy import stats
from scipy.stats import chi2_contingency
import numpy as np
import matplotlib.pyplot as plt 
import pandas as pd

engine = create_engine(f"sqlite:///./{os.environ["DB_NAME"]}", echo=True)

def get_data(engine):

    numerical_attribute_dict = {
        "age": [],
        "household_size": [],
        "budget_eat_out": [],
        "budget_takeout_delivery": [],
        "grocery_cost": [],
        # "health_consciousness": [],
        # "frequency_eating_out": [],
        # "frequency_takeout_delivery": [],
        # "frequency_cook_home": [],
        # "frequency_grocery": [],
    }

    categorical_attribute_dict = {
        "gender": set(),
        "relationship_status": set(),
        "employment_status": set(),
        "monthly_income": set(),
        "pet_ownership": set(),
        "housing_type": set(),
        "primary_cook": set(),
        "preferred_dining": set(),
        "health_consciousness": set(),
        "frequency_eating_out": set(),
        "frequency_takeout_delivery": set(),
        "frequency_cook_home": set(),
        "frequency_grocery": set(),
    }

    with Session(engine) as session:
        select_all_respondents = select(Respondents)
        for respondent in session.scalars(select_all_respondents):
            numerical_attribute_dict["age"].append(respondent.age)
            numerical_attribute_dict["household_size"].append(respondent.household_size)
            numerical_attribute_dict["budget_eat_out"].append(respondent.budget_eat_out)
            numerical_attribute_dict["budget_takeout_delivery"].append(respondent.budget_takeout_delivery)
            numerical_attribute_dict["grocery_cost"].append(respondent.grocery_cost)
            # numerical_attribute_dict["health_consciousness"].append(respondent.health_consciousness)
            # numerical_attribute_dict["frequency_eating_out"].append(respondent.frequency_eating_out)
            # numerical_attribute_dict["frequency_takeout_delivery"].append(respondent.frequency_takeout_delivery)
            # numerical_attribute_dict["frequency_cook_home"].append(respondent.frequency_cook_home)
            # numerical_attribute_dict["frequency_grocery"].append(respondent.frequency_grocery)
            categorical_attribute_dict["gender"].add(respondent.gender)
            categorical_attribute_dict["relationship_status"].add(respondent.relationship_status)
            categorical_attribute_dict["employment_status"].add(respondent.employment_status)
            categorical_attribute_dict["monthly_income"].add(respondent.monthly_income)
            categorical_attribute_dict["pet_ownership"].add(respondent.pet_ownership)
            categorical_attribute_dict["housing_type"].add(respondent.housing_type)
            categorical_attribute_dict["primary_cook"].add(respondent.primary_cook)
            categorical_attribute_dict["preferred_dining"].add(respondent.preferred_dining)
    data_dict = {
        "numerical_attribute_dict": numerical_attribute_dict.copy(),
        "categorical_attribute_dict": categorical_attribute_dict.copy()
    }
    return data_dict

def pearsons(data_dict):
    numerical_attribute_dict = data_dict[numerical_attribute_dict]
    pearsons_dict = {}

    for key in numerical_attribute_dict.keys():
        plt.hist(numerical_attribute_dict[key])
        plt.savefig(f"histograms/histogram-{key}.png")
        for key2 in numerical_attribute_dict.keys():
            res = stats.pearsonr(numerical_attribute_dict[key], numerical_attribute_dict[key2])
            if pearsons_dict.get(key) is None:
                pearsons_dict[key] = {}
        
            if pearsons_dict[key].get(key2) is None:
                if key == key2:
                    pearsons_dict[key][key2] = None
                else:
                    pearsons_dict[key][key2] = round(res.statistic, 2)


    with open("numerical_correlations.csv", "w") as f:
        f.write(f",{",".join(numerical_attribute_dict.keys())}\n")
        for key in pearsons_dict.keys():
            f.write(key)
            for key2 in pearsons_dict.keys():
                f.write(f",{pearsons_dict[key][key2]}")
            f.write("\n")

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

def get_attr_values(engine):
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
    print(categorical_dict_counts)

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

# chi_square(engine, categorical_dict["gender"], categorical_dict["relationship_status"])
# data_dict = get_data(engine)
# pearsons(data_dict)
get_attr_values(engine)