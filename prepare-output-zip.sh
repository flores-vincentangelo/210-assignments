#!/usr/bin/bash

# rsync -avz ./Flores_Espinar_A3_Code.py ~/school/Flores_Espinar_A3/
# rsync -avz ./Flores_Espinar_FactorsInfluencingDiningChoice.csv ~/school/Flores_Espinar_A3/
rsync -avz ./README.md ~/school/Flores_Espinar_A3/
rsync -avz --exclude=__pycache__ ./dataETL ~/school/Flores_Espinar_A3/
rsync -avz ./requirements.txt ~/school/Flores_Espinar_A3/
rsync -avz ./setupDb.py ~/school/Flores_Espinar_A3/
# rsync -avz ./Flores_Espinar_A3_Ans.pdf ~/school/Flores_Espinar_A3/
cd ..
zip -r Flores_Espinar_A3.zip Flores_Espinar_A3