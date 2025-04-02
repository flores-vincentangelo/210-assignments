import os
import matplotlib.pyplot as plt 
import json
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from dataETL.dataModel import Respondents
from scipy import stats

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
    data_dict = numerical_attribute_dict.copy()
    return data_dict

def pearsons(data_dict):
    numerical_attribute_dict = data_dict
    pearsons_dict = {}
    pearsons_list = []

    for attr1 in numerical_attribute_dict.keys():
        plt.hist(numerical_attribute_dict[attr1])
        plt.savefig(f"histograms/histogram-{attr1}.png")
        pearsons_dict[attr1] = {}
        for attr2 in numerical_attribute_dict.keys():
            if attr1 == attr2:
                continue
            elif attr2 in pearsons_dict:
                continue;
            
            res = stats.pearsonr(numerical_attribute_dict[attr1], numerical_attribute_dict[attr2])
        
            pearsons_dict[attr1][attr2] = round(res.statistic, 2)
            pearsons_list.append({
                "attributes": [attr1, attr2],
                "statistic": round(res.statistic, 2)
            })

    # with open("numerical_correlations.csv", "w") as f:
    #     f.write(f",{",".join(numerical_attribute_dict.keys())}\n")
    #     for attr1 in pearsons_dict.keys():
    #         f.write(attr1)
    #         for attr2 in pearsons_dict.keys():
    #             f.write(f",{pearsons_dict[attr1][attr2]}")
    #         f.write("\n")
    return pearsons_list

data_dict = get_data(engine)
pearsons_list = pearsons(data_dict)
def sorting_function(obj):
    return obj["statistic"]
pearsons_list.sort(key=sorting_function, reverse=True)
with open("attr_pearsons_list.json", "w") as f:
    f.write(json.dumps(pearsons_list))
with open("pearsons_list.csv", "w") as f:
    f.write(f"Attribute 1,Attribute 2,Correlation Coefficient,Rank\n")
    count = 1
    for dict in pearsons_list:
        f.write(f"{dict["attributes"][0]},{dict["attributes"][1]},{dict["statistic"]},{count}\n")
        count += 1