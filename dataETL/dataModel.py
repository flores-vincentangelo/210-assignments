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
