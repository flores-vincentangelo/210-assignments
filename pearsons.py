import os
import matplotlib.pyplot as plt 
import json
import numpy as np
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from dataETL.dataModel import Respondents
from scipy import stats
from tabulate import tabulate

engine = create_engine(f"sqlite:///./{os.environ["DB_NAME"]}", echo=False)

analysis_path = "analysis/pearsons"
if not os.path.exists(analysis_path):
        os.makedirs(analysis_path)

def get_data(engine):

    numerical_attribute_dict = {
        "age": [],
        "household_size": [],
        "budget_eat_out": [],
        "budget_takeout_delivery": [],
        "grocery_cost": [],
    }

    with Session(engine) as session:
        select_all_respondents = select(Respondents)
        for respondent in session.scalars(select_all_respondents):
            numerical_attribute_dict["age"].append(respondent.age)
            numerical_attribute_dict["household_size"].append(respondent.household_size)
            numerical_attribute_dict["budget_eat_out"].append(respondent.budget_eat_out)
            numerical_attribute_dict["budget_takeout_delivery"].append(respondent.budget_takeout_delivery)
            numerical_attribute_dict["grocery_cost"].append(respondent.grocery_cost)
    return numerical_attribute_dict

def make_scatter_plots(x_label, y_label, x, y):
    figure_path = "figures/pearsons-scatter"
    if not os.path.exists(figure_path):
        os.makedirs(figure_path)
    fig, ax = plt.subplots()
    # plt.style.use('_mpl-gallery')
    sizes = np.random.uniform(15, 80, len(x))
    colors = np.random.uniform(15, 80, len(x))
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    ax.scatter(x, y, s=sizes, c=colors, vmin=0, vmax=100)
    plt.savefig(f"{figure_path}/scatter-{x_label}-{y_label}.png")
    plt.close()


def make_histogram(numerical_attribute_dict, attribute):
    figure_path = "figures/histogram"
    if not os.path.exists(figure_path):
        os.makedirs(figure_path)
    plt.xlabel(attribute)
    plt.ylabel("frequency")
    plt.hist(numerical_attribute_dict[attribute])
    plt.savefig(f"{figure_path}/histogram-{attribute}.png")
    plt.close()
    # if attribute == "budget_eat_out":
        # plt.show()

def pearsons_correlation(data_dict):
    numerical_attribute_dict = data_dict
    pearsons_dict = {}
    pearsons_list = []

    for attr1 in numerical_attribute_dict.keys():
        pearsons_dict[attr1] = {}
        for attr2 in numerical_attribute_dict.keys():
            if attr1 == attr2:
                continue
            elif attr2 in pearsons_dict:
                continue;
            res = stats.pearsonr(numerical_attribute_dict[attr1], numerical_attribute_dict[attr2])
            pearsons_dict[attr1][attr2] = round(res.statistic, 2)
            pearsons_list.append({
                "attributes": [{
                    "name": attr1,
                    "values": data_dict[attr1]
                }, {
                    "name": attr2,
                    "values": data_dict[attr2]
                }],
                "statistic": round(res.statistic, 2)
            })

    return pearsons_list

def pretty_print(pearsons_list, to_csv=False):
    f = open(f"{analysis_path}/pearsons_list.csv", "w") if to_csv else None
    table = []
    table.append(["Attribute 1","Attribute 2","Correlation Coefficient","Rank"])
    if to_csv:
        f.write(f"Attribute 1,Attribute 2,Correlation Coefficient,Rank\n")
    count = 1
    for obj in pearsons_list:
        attr1 = obj["attributes"][0]
        attr2 = obj["attributes"][1]
        if to_csv:
            f.write(f"{attr1["name"]},{attr2["name"]},{obj["statistic"]},{count}\n")
        table.append([attr1["name"],attr2["name"],obj["statistic"],count])
        count += 1
    print(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))
    if to_csv:
        f.close()

numerical_data_dict = get_data(engine)
pearsons_list = pearsons_correlation(numerical_data_dict)

for attr in numerical_data_dict.keys():
    make_histogram(numerical_data_dict, attr)
for obj in pearsons_list:
    attr1 = obj["attributes"][0]
    attr2 = obj["attributes"][1]
    make_scatter_plots(attr1["name"], attr2["name"], attr1["values"], attr2["values"])



with open(f"{analysis_path}/attr_pearsons_list.json", "w") as f:
    f.write(json.dumps(pearsons_list))
# with open(f"{analysis_path}/pearsons_list.csv", "w") as f:
#     f.write(f"Attribute 1,Attribute 2,Correlation Coefficient,Rank\n")
#     count = 1
#     for obj in pearsons_list:
#         attr1 = obj["attributes"][0]
#         attr2 = obj["attributes"][1]
#         f.write(f"{attr1["name"]},{attr2["name"]},{obj["statistic"]},{count}\n")
#         count += 1

pretty_print(pearsons_list)