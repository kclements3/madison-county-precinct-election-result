import sys
import pandas as pd
from difflib import SequenceMatcher
import pdfplumber


# Take pdf of precinct number and results by precinct name
f1 = sys.argv[1] # Results excel file
f2 = sys.argv[2] # Polling place pdf

# Return header of precinct numbers (1st row) and polling places (2nd row)
# 3rd row will contain names from polling results

df1 = pd.read_excel(f1, engine='xlrd')
precinct_names_from_results = df1.columns[3:]

precint_pdf = pdfplumber.open(f2)

precint_number_tbl = []
for page in precint_pdf.pages:
    precint_number_tbl += page.extract_table()

match_dict = {}
precint_num_name_map = {}

# Match polling places to precinct numbers
for row in precint_number_tbl[1:]:
    # skip first row
    pNum = row[0]
    pName = row[1]

    match_dict[pNum] = {pName: []}

    # Loop over each column name and estimate match
    for name in precinct_names_from_results:
        match_dict[pNum][pName].append((name, SequenceMatcher(None, name.lower(), pName.lower()).ratio()))

    # Sort by match
    match_dict[pNum][pName] = sorted(match_dict[pNum][pName], key=lambda item: item[1], reverse=True)

# Order by highest match ratio and return first match
match_dict = dict(sorted(match_dict.items(), key=lambda item: list(item[1].values())[0][0][1], reverse=True))
placesUsed = []
for pNum, matches in match_dict.items():
    ind_to_use = 0
    if len(placesUsed) > 0:
        while list(matches.values())[0][ind_to_use][0] in placesUsed:
            ind_to_use += 1
    precint_num_name_map[list(matches.values())[0][ind_to_use][0]] = pNum
    placesUsed.append(list(matches.values())[0][ind_to_use][0])
    print(list(matches.values())[0][ind_to_use][0], pNum, matches.keys())