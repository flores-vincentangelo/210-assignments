from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Base(DeclarativeBase):
    pass

class DataModel(Base):
    __tablename__ = "data"

    id: Mapped[int] = mapped_column(primary_key=True)
    time_stamp: Mapped[int]
    gender: Mapped[str]
    age: Mapped[int]
    relationship_status: Mapped[str]
    employment_status: Mapped[str]
    monthly_income: Mapped[str]
    health_consciousness: Mapped[int]
    pet_ownership: Mapped[str]
    housing_type: Mapped[str]
    household_size: Mapped[int]
    primary_cook: Mapped[str]
    preferred_dining: Mapped[str]
    budget_eat_out: Mapped[int]
    budget_takeout_delivery: Mapped[int]
    grocery_cost: Mapped[int]
    frequency_eating_out: Mapped[int]
    frequency_takeout_delivery: Mapped[int]
    frequency_cook_home: Mapped[int]
    frequency_grocery: Mapped[int]
    favorite_restaurants: Mapped[str]
    cuisine_choices: Mapped[str]
    restaurant_factors: Mapped[str]

class DataModel2:
    def __init__(self, time_stamp, gender, age, relationship_status, employment_status, monthly_income, health_consciousness, pet_ownership, housing_type, household_size, primary_cook, preferred_dining, budget_eat_out, budget_takeout_delivery, grocery_cost, frequency_eating_out, frequency_takeout_delivery, frequency_cook_home, frequency_grocery, favorite_restaurants, cuisine_choices, restaurant_factors):
        self.time_stamp = time_stamp
        self.gender = self.formatStrings(gender)    
        self.age = self.formatInts(age)
        self.relationship_status = self.formatStrings(relationship_status)
        self.employment_status = self.formatStrings(employment_status)
        self.monthly_income = self.formatStrings(monthly_income)
        self.health_consciousness = self.formatInts(health_consciousness)
        self.pet_ownership = self.formatStrings(pet_ownership)
        self.housing_type = self.formatStrings(housing_type)
        self.household_size = self.formatInts(household_size)
        self.primary_cook = self.formatStrings(primary_cook)
        self.preferred_dining = self.formatStrings(preferred_dining)
        self.budget_eat_out = self.formatInts(budget_eat_out)
        self.budget_takeout_delivery = self.formatInts(budget_takeout_delivery)
        self.grocery_cost = self.formatInts(grocery_cost)
        self.frequency_eating_out = self.formatInts(frequency_eating_out)
        self.frequency_takeout_delivery = self.formatInts(frequency_takeout_delivery)
        self.frequency_cook_home = self.formatInts(frequency_cook_home)
        self.frequency_grocery = self.formatInts(frequency_grocery)
        self.favorite_restaurants = self.formatStrings(favorite_restaurants)
        self.cuisine_choices = self.formatStrings(cuisine_choices)
        self.restaurant_factors = self.formatStrings(restaurant_factors)

    def formatStrings(self, testString):
        return testString.replace("\"", "")
    
    def formatInts(self, testString):
        if testString == 'N/A':
            return None
        elif isinstance(testString, int):
            return testString
        elif isinstance(testString, str):
            testString = testString.replace(",", "").replace("\"", "")
            return int(testString)
        
