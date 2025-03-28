import os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from dataETL.dataModel import Respondents
from scipy import stats
import matplotlib.pyplot as plt 
import pandas as pd

x, y = [1, 2, 3, 4, 5, 6, 7], [10, 9, 2.5, 6, 4, 3, 2]
res = stats.pearsonr(x, y)
print(res.statistic)


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


engine = create_engine(f"sqlite:///./{os.environ["DB_NAME"]}", echo=True)
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

