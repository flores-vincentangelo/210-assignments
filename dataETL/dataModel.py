from typing import List
from sqlalchemy import ForeignKey, Column, Table, Integer
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

respondent_cuisine = Table(
    "respondent_cuisine",
    Base.metadata,
    Column("respondent_id", Integer, ForeignKey("respondents.id")),
    Column("cuisine_id",Integer, ForeignKey("cuisine.id"))
)

respondent_restaurant_factors = Table(
    "respondent_restaurant_factors",
    Base.metadata,
    Column("respondent_id", Integer, ForeignKey("respondents.id")),
    Column("restaurant_factors_id", Integer, ForeignKey("restaurant_factors.id"))
)

class Respondents(Base):
    __tablename__ = "respondents"

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
    cuisine_choices_str: Mapped[str]
    restaurant_factors_str: Mapped[str]  
    cuisine_choices: Mapped[List["Cuisine"]] = relationship(
        argument="Cuisine", 
        secondary=respondent_cuisine, 
        back_populates="respondents")
    restaurant_factors: Mapped[List["RestaurantFactors"]] = relationship(
        argument="RestaurantFactors", 
        secondary=respondent_restaurant_factors, 
        back_populates="respondents")

    def __repr__(self):
        return f"Respondents(id: {self.id} gender: {self.gender} age: {self.age})"

class DataMapping:
    
    hc_dict = {
        1: "Very health conscious",
        2: "Somewhat health conscious",
        3: "Not health conscious"
    }
    
    frequency_1 = {
        1 : "all meals every day",
        2 : "1 - 2 times per day",
        3 : "3 - 6 times per week",
        4 : "1 - 2 times per week",
        5 : "Once every two weeks",
        6 : "Once a month",
        7 : "Occasionally/rarely"
    }

    frequency_2 = {
        1 : "Once a week",
        2 : "Twice a month",
        3 : "Once a month",
        4 : "No definite frequency"
    }

    def health_consciousness(self,num):
        return self.hc_dict[num]
    
    def frequency_1(self, num):
        return self.frequency_1[num]
    
    def frequency_2(self, num):
        return self.frequency_2(num)

attribute_column_dict = {
    "age": "Age",
    "household_size":"Household Size",
    "budget_eat_out":"Average budget per person when eating out",
    "budget_takeout_delivery":"Average budget per person when ordering takeout/delivery",
    "grocery_cost":"Approximate cost of groceries per month for home cooking",
    "gender": "Gender",
    "relationship_status": "Relationship Status",
    "employment_status": "Employment Status",
    "pet_ownership": "Pet Ownership",
    "housing_type": "Housing type",
    "primary_cook": "Are you the primary person that prepares meals in the household if any?",
    "preferred_dining": "Preferred Dining",
    "frequency_eating_out": "Frequency of eating out",
    "frequency_takeout_delivery": "Frequency of ordering takeout/delivery",
    "frequency_cook_home": "Frequency of cooking at home",
    "frequency_grocery": "Frequency of buying groceries",
}

class Cuisine(Base):
    __tablename__ = "cuisine"

    id: Mapped[int] = mapped_column(primary_key=True)
    cuisine: Mapped[str]
    respondents: Mapped[List["Respondents"]] = relationship(secondary=respondent_cuisine, back_populates="cuisine_choices")
    
    def __repr__(self):
        return f"Cuisine(id: {self.id} cuisine: {self.cuisine})"
    
class RestaurantFactors(Base):
    __tablename__ = "restaurant_factors"

    id: Mapped[int] = mapped_column(primary_key=True)
    factor: Mapped[str]
    respondents: Mapped[List["Respondents"]] = relationship(secondary=respondent_restaurant_factors, back_populates="restaurant_factors")

    def __repr__(self):
        return f"Cuisine(id: {self.id} factor: {self.factor})"
