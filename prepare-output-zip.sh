#!/usr/bin/bash

rsync -avz ./Flores_Espinar_A2_Code.py ~/school/Flores_Espinar_A2/
rsync -avz ./Flores_Espinar_FactorsInfluencingDiningChoice.csv ~/school/Flores_Espinar_A2/
rsync -avz ./README.md ~/school/Flores_Espinar_A2/
rsync -avz --exclude=__pycache__ ./dataETL ~/school/Flores_Espinar_A2/
rsync -avz ./requirements.txt ~/school/Flores_Espinar_A2/
rsync -avz ./setupDb.py ~/school/Flores_Espinar_A2/