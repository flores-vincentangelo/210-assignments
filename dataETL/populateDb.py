import re
from sqlalchemy import select
from dataETL.dataModel import Respondents, Cuisine, RestaurantFactors
from sqlalchemy.orm import Session

def format_strings(testString):
        return testString.replace("\"", "")
    
def format_ints(testString):
    if testString == 'N/A':
        return -1
    elif isinstance(testString, int):
        return testString
    elif isinstance(testString, str):
        testString = testString.replace(",", "").replace("\"", "")
        return int(testString)

def populate_db(engine):
    insert_cuisine_choices(engine)
    insert_restaurant_factors(engine)
    insert_respondents_no_cuisinsine_and_res_factors(engine)
    insert_respondents_cuisine_and_rest_factors(engine)

def insert_respondents_no_cuisinsine_and_res_factors(engine):
    insertList = []
    with open("dataset-partially-cleaned.csv", "r") as f:
        for line in f:
            pattern = r',(?=(?:[^"]*"[^"]*")*[^"]*$)'
            result = re.split(pattern,line)

            time_stamp = result[0]
            gender = result[1]
            age = result[2]
            relationship_status = result[3]
            employment_status = result[4]
            monthly_income = result[5]
            health_consciousness = result[6]
            pet_ownership = result[7]
            housing_type = result[8]
            household_size = result[9]
            primary_cook = result[10]
            preferred_dining = result[11]
            budget_eat_out = result[12]
            budget_takeout_delivery = result[13]
            grocery_cost = result[14]
            frequency_eating_out = result[15]
            frequency_takeout_delivery = result[16]
            frequency_cook_home = result[17]
            frequency_grocery = result[18]
            favorite_restaurants = result[19]
            cuisine_choices_str = result[20]
            restaurant_factors_str  = result[21]

            data = Respondents(
            time_stamp = time_stamp,
            gender = format_strings(gender),
            age = format_ints(age),
            relationship_status = format_strings(relationship_status),
            employment_status = format_strings(employment_status),
            monthly_income = format_strings(monthly_income),
            health_consciousness = format_ints(health_consciousness),
            pet_ownership = format_strings(pet_ownership),
            housing_type = format_strings(housing_type),
            household_size = format_ints(household_size),
            primary_cook = format_strings(primary_cook),
            preferred_dining = format_strings(preferred_dining),
            budget_eat_out = format_ints(budget_eat_out),
            budget_takeout_delivery = format_ints(budget_takeout_delivery),
            grocery_cost = format_ints(grocery_cost),
            frequency_eating_out = format_ints(frequency_eating_out),
            frequency_takeout_delivery = format_ints(frequency_takeout_delivery),
            frequency_cook_home = format_ints(frequency_cook_home),
            frequency_grocery = format_ints(frequency_grocery),
            favorite_restaurants = format_strings(favorite_restaurants),
            cuisine_choices_str = format_strings(cuisine_choices_str),
            restaurant_factors_str = format_strings(restaurant_factors_str)
        )

            insertList.append(data)

    with Session(engine) as session:
         session.add_all(insertList)
         session.commit()

cuisine_list = [
    "Asian",
    "Filipino",
    "Korean",
    "Japanese",
    "Mexican",
    "Thai",
    "Vietnamese",
    "Middle Eastern",
    "Indian",
    "Persian",
    "American",
    "Vegetarian",
    "European",
    "Italian",
    "Greek",
    "Other",
]

def insert_cuisine_choices(engine):
    insert_list = []
    for cuisine in cuisine_list:
        c = Cuisine(cuisine = cuisine)
        insert_list.append(c)

    with Session(engine) as session:
         session.add_all(insert_list)
         session.commit()

factors_list = [
    "Instagrammability/Aesthetic",
    "Food Taste",
    "Cost",
    "Accessibility",
    "Occasion",
    "Menu Variety",
    "Healthy Options",
    "Promos",
    "Brand",
    "Pet Accommodation",
    "Ability to accommodate dietary restrictions",
    "Social Media/Reviews",
    "Experience",
    "Other", 
]

def insert_restaurant_factors(engine):
    insert_list = []
    for factor in factors_list:
        f = RestaurantFactors(factor = factor)
        insert_list.append(f)
    with Session(engine) as session:
        session.add_all(insert_list)
        session.commit()

def insert_respondents_cuisine_and_rest_factors(engine):
    with Session(engine) as session:
        cuisine_dict = {}
        cuisine_select_all = select(Cuisine)
        for cuisine in session.scalars(cuisine_select_all):
            cuisine_dict[cuisine.cuisine] = cuisine

        rest_factors_dict = {}
        restaurant_factor_select_all = select(RestaurantFactors)
        for rf in session.scalars(restaurant_factor_select_all):
            rest_factors_dict[rf.factor] = rf
        
        select_all_respondents = select(Respondents)
        for respondent in session.scalars(select_all_respondents):
                cuisine_list = respondent.cuisine_choices_str.split(",")
                restaurant_factor_list = respondent.restaurant_factors_str.split(",")
                
                for cuisine in cuisine_list:
                    respondent.cuisine_choices.append(cuisine_dict[cuisine.strip()])
                
                for rf in restaurant_factor_list:
                    respondent.restaurant_factors.append(rest_factors_dict[rf.strip().replace("\n", "")])

        session.commit()