import re
import os
from dataModel import DataModel
from sqlalchemy.orm import Session
from sqlalchemy import create_engine



def formatStrings(testString):
        return testString.replace("\"", "")
    
def formatInts(testString):
    if testString == 'N/A':
        return -1
    elif isinstance(testString, int):
        return testString
    elif isinstance(testString, str):
        testString = testString.replace(",", "").replace("\"", "")
        return int(testString)

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
        cuisine_choices = result[20]
        restaurant_factors  = result[21]

        data = DataModel(
            time_stamp = time_stamp,
            gender = formatStrings(gender),
            age = formatInts(age),
            relationship_status = formatStrings(relationship_status),
            employment_status = formatStrings(employment_status),
            monthly_income = formatStrings(monthly_income),
            health_consciousness = formatInts(health_consciousness),
            pet_ownership = formatStrings(pet_ownership),
            housing_type = formatStrings(housing_type),
            household_size = formatInts(household_size),
            primary_cook = formatStrings(primary_cook),
            preferred_dining = formatStrings(preferred_dining),
            budget_eat_out = formatInts(budget_eat_out),
            budget_takeout_delivery = formatInts(budget_takeout_delivery),
            grocery_cost = formatInts(grocery_cost),
            frequency_eating_out = formatInts(frequency_eating_out),
            frequency_takeout_delivery = formatInts(frequency_takeout_delivery),
            frequency_cook_home = formatInts(frequency_cook_home),
            frequency_grocery = formatInts(frequency_grocery),
            favorite_restaurants = formatStrings(favorite_restaurants),
            cuisine_choices = formatStrings(cuisine_choices),
            restaurant_factors = formatStrings(restaurant_factors)
        )

        insertList.append(data)

engine = create_engine(f"sqlite:///./{os.environ["DB_NAME"]}", echo=True)
with Session(engine) as session:
     session.add_all(insertList)
     session.commit()