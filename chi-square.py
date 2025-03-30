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
    
    for attr1 in column_attr_list:
        categorical_attr_mappings[attr1] = {}
        for attr2 in column_attr_list:
            if attr1 == attr2:
                continue
            if attr2 in categorical_attr_mappings:
                continue
            categorical_attr_mappings[attr1][attr2] = {}
            for value1 in column_attr_values_dict[attr1]:
                categorical_attr_mappings[attr1][attr2][value1] = {}
                for value2 in column_attr_values_dict[attr2]:
                    categorical_attr_mappings[attr1][attr2][value1][value2] = 0
    return categorical_attr_mappings

def get_totals(engine, categorical_attributes_list, categorical_attr_mappings):
    
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
                        x = f"{column_attr.key} {column_attr2.key} {result_tuple}"
                        if column_attr2.key in categorical_attr_mappings[column_attr.key]:
                            categorical_attr_mappings[column_attr.key][column_attr2.key][result_tuple[0]][result_tuple[1]] = result_tuple[2]
                            f.write(f"{x}\n")
    return categorical_attr_mappings

def chi_square(array):
    critical_value_dict = {
        1:3.841  ,
        2:  5.991,
        3:  7.815,
        4:  9.488,
        5: 11.070,
        6: 12.592,
        7: 14.067,
        8: 15.507,
        9: 16.919,
        10: 18.307,
        11: 19.675,
        12: 21.026,
        13: 22.362,
        14: 23.685,
        15: 24.996,
        16: 26.296,
        17: 27.587,
        18: 28.869,
        19: 30.144,
        20: 31.410,
        21: 32.671,
        22: 33.924,
        23: 35.172,
        24: 36.415,
        25: 37.652,
        26: 38.885,
        27: 40.113,
        28: 41.337,
        29: 42.557,
        30: 43.773,
        31: 44.985,
        32: 46.194,
        33: 47.400,
        34: 48.602,
        35: 49.802,
        36: 50.998,
        37: 52.192,
        38: 53.384,
        39: 54.572,
        40: 55.758,
        41: 56.942,
        42: 58.124,
        43: 59.304,
        44: 60.481,
        45: 61.656,
        46: 62.830,
        47: 64.001,
        48: 65.171,
        49: 66.339,
        50: 67.505,
        51: 68.669,
        52: 69.832,
        53: 70.993,
        54: 72.153,
        55: 73.311,
        56: 74.468,
        57: 75.624,
        58: 76.778,
        59: 77.931,
        60: 79.082,
        61: 80.232,
        62: 81.381,
        63: 82.529,
        64: 83.675,
        65: 84.821,
        66: 85.965,
        67: 87.108,
        68: 88.250,
        69: 89.391,
        70: 90.531,
        71: 91.670,
        72: 92.808,
        73: 93.945,
        74: 95.081,
        75: 96.217,
        76: 97.351,
        77: 98.484,
        78: 99.617,
        79:100.749,
        80:101.879,
        81:103.010,
        82:104.139,
        83:105.267,
        84:106.395,
        85:107.522,
        86:108.648,
        87:109.773,
        88:110.898,
        89:112.022,
        90:113.145,
        91:114.268,
        92:115.390,
        93:116.511,
        94:117.632,
        95:118.752,
        96:119.871,
        97:120.990,
        98:122.108,
        99:123.225,
        100:124.342, 
    }

    obs = np.array(array)
    res = chi2_contingency(obs, correction=False)
    # print(f"statistic {res.statistic}")
    res.pvalue
    # print(f"dof {res.dof}")
    res.expected_freq
    null_hypothesis = ''
    if res.statistic > critical_value_dict[res.dof]:
        # print("reject null hypothesis i.e. values are related")
        null_hypothesis = 'Reject. Values related'
    else:
        # print("accept null hypothesis i.e. values are unrelated")
        null_hypothesis = 'Accept. Values unrelated'

    return tuple((
        res.statistic,
        res.dof,
        null_hypothesis
    ))

def chi_square_analysis(cat_att_maps):
    chi_square_dict = {}
    for attr1 in cat_att_maps.keys():  
        if cat_att_maps[attr1].keys() == 0:
            continue
        chi_square_dict[attr1] = {}
        for attr2 in cat_att_maps[attr1].keys():
            chi_square_list = []
            for attr1_values in cat_att_maps[attr1][attr2].keys():
                value2_list = []
                for attr2_values in cat_att_maps[attr1][attr2][attr1_values].keys():
                    value2_list.append(cat_att_maps[attr1][attr2][attr1_values][attr2_values])
                
                chi_square_list.append(value2_list)
            
            (statistic, dof, null_hypothesis) = chi_square(chi_square_list)
            chi_square_dict[attr1][attr2] = {
                "statistic": statistic,
                "dof": dof,
                "null_hypothesis": null_hypothesis
            }
            if (null_hypothesis == "Reject. Values related"):
                print(f"{attr1} {attr2} are related!")
    
    return chi_square_dict

        
            

categorical_attr_mappings = prepare_attr_mapping(engine, categorical_attributes_list)
categorical_attr_mappings = get_totals(engine, categorical_attributes_list, categorical_attr_mappings)
with open("categorical_attr.json", "w") as f:
    f.write(json.dumps(categorical_attr_mappings))
chi_square_dict = chi_square_analysis(categorical_attr_mappings)
with open("chi_square_dict.json", "w") as f:
    f.write(json.dumps(chi_square_dict))

