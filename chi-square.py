import json
import os
import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, func, inspect, select
from sqlalchemy.orm import Session
from dataETL.dataModel import Respondents
from scipy.stats import chi2_contingency

engine = create_engine(f"sqlite:///./{os.environ["DB_NAME"]}", echo=True)

categorical_attributes_list = [
    "gender",
    "relationship_status",
    "employment_status",
    "pet_ownership",
    "housing_type",
    "primary_cook",
    "preferred_dining",
]

def get_cat_attr_combinations(engine, categorical_attributes_list):

    # This method assembles the dictionary for all combinations of categorical attributes
    # and the set of all categorical values used in each of the columns.
    # The method returns a dictionary of all combinations of categorical attributes and their values 
    # and initializes their counts to 0. 
    # An example using "gender" and "relationship_status" is shown below:
    """ 
    {
        "gender": {
            "relationship_status": {
                "Female": {
                    "Married": 0,
                    "Married but not living together": 0,
                    "Single": 0
                },
                "Male": {
                    "Married": 0,
                    "Married but not living together": 0,
                    "Single": 0
                }
            },
            "employment_status": {...},
            "pet_ownership": {...},
            ...
        },
        "relationship_status": {...},
        ...  
    }
     """
    categorical_attr_mappings = {}
    column_attr_values_dict = {}

    # get metadata of "Respondents" table
    mapper = inspect(Respondents)

    # get all unique categorical value found for each attribute/column of the table
    # this is done by selecting the columnn and grouping by itself, therefore getting all unique values.
    # "mapper.attrs" gets all column entities of the "Respondents" table
    for column_attr in mapper.attrs:
        if column_attr.key not in categorical_attributes_list:
            continue

        column_attr_values_dict[column_attr.key] = []

        with Session(engine) as session:
            # grouping query
            query = select(column_attr).group_by(column_attr)
            for result_tuple in session.execute(query):
                column_attr_values_dict[column_attr.key].append(result_tuple[0])
    
    # assembly of categorical attribute dictionary
    for attr1 in column_attr_values_dict.keys():
        categorical_attr_mappings[attr1] = {}
        for attr2 in column_attr_values_dict.keys():
            
            # skip getting of correlation when attributes are the same
            if attr1 == attr2:
                continue

            # this condition is to prevent computing the same pair of attributes twice.
            # ex. "gender" "relationship_status" <==> "relationship_status" "gender" 
            if attr2 in categorical_attr_mappings:
                continue

            categorical_attr_mappings[attr1][attr2] = {}

            for value1 in column_attr_values_dict[attr1]:
                categorical_attr_mappings[attr1][attr2][value1] = {}
                for value2 in column_attr_values_dict[attr2]:
                    categorical_attr_mappings[attr1][attr2][value1][value2] = 0

    return categorical_attr_mappings

def get_counts(engine, categorical_attributes_list, categorical_attr_mappings):
    
    # this method gets the values for each combination of values for each combination of attributes
    # assembling the dictionary must be done first because the query below omits groupings where their value is 0

    mapper = inspect(Respondents)
    for column_attr in mapper.attrs:
        for column_attr2 in mapper.attrs:
            if column_attr.key not in categorical_attributes_list or column_attr2.key not in categorical_attributes_list:
                continue
            
            if column_attr.key == column_attr2.key:
                continue

            if column_attr2.key not in categorical_attr_mappings[column_attr.key]:
                continue

            group_by_query = select(column_attr, column_attr2, func.count(column_attr).label("count")).group_by(column_attr).group_by(column_attr2)
            with Session(engine) as session:
                for result_tuple in session.execute(group_by_query):
                    categorical_attr_mappings[column_attr.key][column_attr2.key][result_tuple[0]][result_tuple[1]] = result_tuple[2]
    
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
    res.pvalue
    res.expected_freq
    null_hypothesis = ''
    if res.statistic > critical_value_dict[res.dof]:
        null_hypothesis = 'Reject. Values related'
    else:
        null_hypothesis = 'Accept. Values unrelated'

    return tuple((
        res.statistic,
        res.dof,
        critical_value_dict[res.dof],
        null_hypothesis,
        obs,
        res.expected_freq
    ))

def chi_square_analysis(cat_att_dict):

    # do the chi square analysis for each pair of attributes
    
    chi_square_dict = {}
    attr_chi_square_list = []

    for attr1 in cat_att_dict.keys():  
        if len(cat_att_dict[attr1].keys()) == 0:
            continue
        chi_square_dict[attr1] = {}
        for attr2 in cat_att_dict[attr1].keys():
            
            # assembling the list of lists for the chi_square function
            chi_square_list = []

            for attr1_values in cat_att_dict[attr1][attr2].keys():
                value2_list = []
                for attr2_values in cat_att_dict[attr1][attr2][attr1_values].keys():
                    value2_list.append(cat_att_dict[attr1][attr2][attr1_values][attr2_values])
                
                chi_square_list.append(value2_list)
            
            # chi square analysis
            (statistic, dof, critical_value, null_hypothesis, obs, expected_freq) = chi_square(chi_square_list)
            chi_square_dict[attr1][attr2] = {
                "statistic": statistic,
                "dof": dof,
                "null_hypothesis": null_hypothesis
            }

            attr_chi_square_list.append({
                "attributes": [attr1, attr2],
                "dof": dof,
                "critical_value": critical_value,
                "statistic": round(statistic, 5),
                "null_hypothesis": null_hypothesis,
                "x_axis":list(cat_att_dict[attr1][attr2][attr1_values].keys()),
                "y_axis":list(cat_att_dict[attr1][attr2].keys()),
                "obs": obs.tolist(),
                "expected": expected_freq.tolist()
            })
            if (null_hypothesis == "Reject. Values related"):
                print(f"{attr1} {attr2} are related!")
    
    return (chi_square_dict, attr_chi_square_list)

        
chi_square_filepath = "analysis/chi_square"
figure_path = "figures/chi_square"
if not os.path.exists(chi_square_filepath):
    os.makedirs(chi_square_filepath)
if not os.path.exists(figure_path):
        os.makedirs(figure_path)   

categorical_attr_mappings = get_cat_attr_combinations(engine, categorical_attributes_list)
categorical_attr_mappings = get_counts(engine, categorical_attributes_list, categorical_attr_mappings)

with open(f"{chi_square_filepath}/categorical_attr_mappings.json", "w") as f:
    f.write(json.dumps(categorical_attr_mappings))

(chi_square_dict, chi_square_list) = chi_square_analysis(categorical_attr_mappings)

# with open(f"{chi_square_filepath}/chi_square_dict.json", "w") as f:
#     f.write(json.dumps(chi_square_dict))

def sorting_function(obj):
    return obj["statistic"]
chi_square_list.sort(key=sorting_function)
with open(f"{chi_square_filepath}/chi_square_list.json", "w") as f:
    f.write(json.dumps(chi_square_list))

for obj in chi_square_list:
    attr1 = obj["attributes"][0]
    attr2 = obj["attributes"][1]
    row_count = len(obj["y_axis"])
    column_count = len(obj["x_axis"])
    header = f"Attributes:,{attr1},{attr2}\nDegree(s) of freedom:,{obj["dof"]}\nCritical value:,{obj["critical_value"]}\nStatistic:,{obj["statistic"]}\n"

    value_comb_list = []
    observed_list = []
    expected_list = []

    with open(f"{chi_square_filepath}/csv-{attr1}-{attr2}.csv", "w") as f:
        f.write(header)
        # f.write("\n,")
        # for x_axis in obj["x_axis"]:
        #     f.write(f"{x_axis},,")
        # f.write("\n,")

        # for x_axis in obj["x_axis"]:
        #     f.write(f"obs,exp,")
        # f.write("\n")

        f.write("\n")
        f.write("attribute combination, observed, expected\n")
        for i in range(row_count):
            for j in range(column_count):
                observed = obj["obs"][i][j]
                expected = obj["expected"][i][j]
                value_combination = f"{obj["y_axis"][i]} {obj["x_axis"][j]}"
                value_comb_list.append(value_combination)
                observed_list.append(observed)
                expected_list.append(expected)
                f.write(f"{obj["y_axis"][i]} {obj["x_axis"][j]},{observed},{expected}\n")
    
    with open(f"{chi_square_filepath}/csv-exp-obs-{attr1}-{attr2}.csv", "w") as f:
        f.write(header)
        f.write("\n,")
        for x_axis in obj["x_axis"]:
            f.write(f"{x_axis},,")
        f.write("\n,")

        for x_axis in obj["x_axis"]:
            f.write(f"obs,exp,")
        f.write("\n")

        for i in range(row_count):
            f.write(f"{obj["y_axis"][i]},")
            for j in range(column_count):
                observed = obj["obs"][i][j]
                expected = obj["expected"][i][j]
                f.write(f"{observed},{expected},")
            f.write("\n")

    fig, ax = plt.subplots()
    plt.xticks(rotation=45, ha="right")
    ax.tick_params(axis='both', labelsize=5)
    ax.plot(value_comb_list, observed_list, 'o-', linewidth=1)
    ax.plot(value_comb_list, expected_list, 'o-', linewidth=1)
    plt.savefig(f"{figure_path}/plot-{attr1}-{attr2}.png")
    plt.close()
                



