import pandas as pd
from pathlib import Path
import sys
from src.PollingData import PollingData

sys.path.append(str(Path(__file__).resolve().parent.parent))
contest_map = {
    2020: 'PRESIDENT AND VICE PRESIDENT OF THE UNITED STATES',
    2022: 'GOVERNOR',
    2024: 'PRESIDENT AND VICE PRESIDENT OF THE UNITED STATES',
    2026: 'GOVERNOR'
}
year_range = range(2020, 2027, 2)
out_df = pd.DataFrame(columns=['Precinct #', 'Latest Location']+list(year_range))
out_df = out_df.set_index('Precinct #')
for year in year_range:
    if year >= 2024:
        shapefile = '../data/shapefiles/precincts_2026_rev2.shp'
    elif year < 2024:
        shapefile = '../data/shapefiles/tl_2020_01_vtd20.shp'
    pollingData = PollingData(year, f'../data/precinct-numbers/{year}-Polling-Locations.pdf',
                               f'../data/madison-county-votes/{year}-General-Madison.xls', shapefile)
    contest = contest_map[year]
    pollingData.match_polling_places()
    pct_data = pollingData.determine_dem_rep_pct(contest, False)
    # pollingData.plot_data('Governor')
    for row in pct_data.iterrows():
        out_df.loc[row[1]['PrecNum'], year] = pd.to_numeric(round(row[1]['pct_repub'],2), errors='coerce')

        out_df.loc[row[1]['PrecNum'], 'Latest Location'] = row[1]['Name']

# out_df.to_html('../pages/summary_table.html')
out_df.sort_values(by='Precinct #')
clean_fmt = lambda x: f'{x:.2f}'.rstrip('0').rstrip('.') if pd.notnull(x) else ''
# html_output = out_df.style.background_gradient(cmap="bwr", subset=list(year_range)).to_html(float_format=clean_fmt)
html_output = (
    out_df.style
    .format(clean_fmt, subset=list(year_range))
    .background_gradient(cmap="bwr", subset=list(year_range))
    .to_html()
)
# Optional: Save to an HTML file
with open("table.html", "w") as f:
    f.write(html_output)
#
# # 2024 polling place 2016 Voters, 2020 Voters, 2024 Voters, 2016 Repub Votes,
# # Precinct #
# df_2016 = pd.read_csv('2016-General-PrecinctLevel/2016-General-Madison-rev1.csv')
# df_2020 = pd.read_csv('2020 General Precinct Results/2020-General-Madison-rev1.csv')
# df_2024 = pd.read_csv('2024-General/2024-General-Madison-Rev1.csv')
#
# df_2016 = df_2016.loc[:, ~df_2016.columns.str.contains('^Unnamed')]
# df_2020 = df_2020.loc[:, ~df_2020.columns.str.contains('^Unnamed')]
# df_2024 = df_2024.loc[:, ~df_2024.columns.str.contains('^Unnamed')]
#
#
# precincts = set(df_2016.columns[3:]).union(df_2020.columns[3:]).union(set(df_2024.columns[3:]))
#
# out_cols = ['2016 Polling Place', '2016 Registered Voters', '2016 Ballots Cast', '2016 Democratic Votes (Hillary)', '2016 Republican Votes (Trump)',
#             '2020 Polling Place', '2020 Registered Voters', '2020 Ballots Cast', '2020 Democratic Votes (Biden)', '2020 Republican Votes (Trump)',
#             '2024 Polling Place', '2024 Registered Voters', '2024 Ballots Cast', '2024 Democratic Votes (Harris)', '2024 Republican Votes (Trump)']
# df = pd.DataFrame(columns=out_cols, index = list(precincts))
#
# for precinct in precincts:
#     if precinct in df_2016.columns[3:]:
#         df.loc[precinct, '2016 Polling Place'] = df_2016[precinct][0]
#         df.loc[precinct, '2016 Registered Voters'] = df_2016[precinct][1]
#         df.loc[precinct, '2016 Ballots Cast'] = df_2016[precinct][2]
#         df.loc[precinct, '2016 Democratic Votes (Hillary)'] = df_2016[precinct][7]
#         df.loc[precinct, '2016 Republican Votes (Trump)'] = df_2016[precinct][8]
#
#     if precinct in df_2020.columns[3:]:
#         df.loc[precinct, '2020 Polling Place'] = df_2020[precinct][0]
#         df.loc[precinct, '2020 Registered Voters'] = df_2020[precinct][1]
#         df.loc[precinct, '2020 Ballots Cast'] = df_2020[precinct][2]
#         df.loc[precinct, '2020 Democratic Votes (Biden)'] = df_2020[precinct][8]
#         df.loc[precinct, '2020 Republican Votes (Trump)'] = df_2020[precinct][9]
#
#     if precinct in df_2024.columns[3:]:
#         df.loc[precinct, '2024 Polling Place'] = df_2024[precinct][0]
#         df.loc[precinct, '2024 Registered Voters'] = df_2024[precinct][1]
#         df.loc[precinct, '2024 Ballots Cast'] = df_2024[precinct][2]
#         df.loc[precinct, '2024 Democratic Votes (Harris)'] = df_2024[precinct][9]
#         df.loc[precinct, '2024 Republican Votes (Trump)'] = df_2024[precinct][10]

# df.to_csv('Summary_Data_2016-2024.csv')