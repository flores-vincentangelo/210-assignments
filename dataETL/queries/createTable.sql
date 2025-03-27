DROP TABLE IF EXISTS data;
CREATE TABLE IF NOT EXISTS data 
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time_stamp INTEGER ,
    gender TEXT,
    age	INTEGER,
    relationship_status TEXT,
    employment_status TEXT,
    monthly_income	TEXT,
    health_consciousness INTEGER,
    pet_ownership TEXT,
    housing_type TEXT,
    household_size INTEGER,
    primary_cook TEXT,
    preferred_dining TEXT,
    budget_eat_out INTEGER,
    budget_takeout_delivery	INTEGER,
    grocery_cost INTEGER,
    frequency_eating_out INTEGER,
    frequency_takeout_delivery INTEGER,
    frequency_cook_home INTEGER,
    frequency_grocery INTEGER,
    favorite_restaurants TEXT,
    cuisine_choices	TEXT,
    restaurant_factors TEXT
);
