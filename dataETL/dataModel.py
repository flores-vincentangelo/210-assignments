from sqlalchemy import ForeignKey
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

    def __repr__(self):
        return f"DataModel(id: {self.id} gender: {self.gender} age: {self.age})"


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

class Cuisine(Base):
    __tablename__ = "cuisine"

    id: Mapped[int] = mapped_column(primary_key=True)
    cuisine: Mapped[str]
    
    def __repr__(self):
        return f"Cuisine(id: {self.id} cuisine: {self.cuisine})"
    
class RestaurantFactors(Base):
    __tablename__ = "restaurant_factors"

    id: Mapped[int] = mapped_column(primary_key=True)
    factor: Mapped[str]

    def __repr__(self):
        return f"Cuisine(id: {self.id} factor: {self.factor})"


class RespondentCuisine(Base):
    __tablename__ = "respondent_cuisine"

    respondent_id: Mapped[int] = mapped_column(ForeignKey("data.id"), primary_key=True)
    cuisine_id: Mapped[int] = mapped_column(ForeignKey("cuisine.id"), primary_key=True)

    def __repr__(self):
        return f"RespondentCuisine(respondent_id: {self.respondent_id} cuisine_id: {self.cuisine_id})"

class RespondentRestFactor(Base):
    __tablename__ = "respondent_restaurant_factor"


    respondent_id: Mapped[int] = mapped_column(ForeignKey("data.id"), primary_key=True)
    factor_id: Mapped[int] = mapped_column(ForeignKey("restaurant_factors.id"), primary_key=True)

    def __repr__(self):
        return f"RespondentRestFactor(respondent_id: {self.respondent_id} factor_id: {self.factor_id})"
