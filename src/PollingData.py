import sys
import plotly.express as px
import pandas as pd
from difflib import SequenceMatcher
import pdfplumber
import geopandas as gpd

class PollingData:
    def __init__(self, year, polling_location_file, results_file, shapefile_path):
        self.year = year
        self.polling_location_file = polling_location_file
        self.results_file = results_file
        self.shape_data = gpd.read_file(shapefile_path)

        self.polling_place_map = {}
        self.df1 = None

    def match_polling_places(self):
        f1 = self.results_file # excel file
        f2 = self.polling_location_file # pdf


        self.df1 = pd.read_excel(f1, engine='xlrd')
        self.df1['Contest Title'] = self.df1['Contest Title'].str.strip()
        precinct_names_from_results = self.df1.columns[3:]
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
                if 'OXR' in name:
                    newname=name.replace('OXR', 'Owens Cross Roads')
                    match_dict[pNum][pName].append((name, SequenceMatcher(None, newname.lower(), pName.lower()).ratio()))
                else:
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

        self.polling_place_map = precint_num_name_map

    def determine_dem_rep_pct(self, contest, primaryFlag=False):
        df2 = self.df1.loc[self.df1['Contest Title']== contest]
        # df2_dem = self.df1.loc[self.df1['Contest Title'] == contest]
        for precinct_name in list(self.df1.columns[3:]):
            if precinct_name not in self.polling_place_map:
                print(f'No match found for {precinct_name}')
                continue
            else:
                precinct_num = self.polling_place_map[precinct_name]
            ind = self.shape_data[self.shape_data['PrecNum'] == precinct_num].index
            totalDemVotes = df2.loc[df2['Party'] == 'DEM', precinct_name].iloc[0]
            totalRepVotes = df2.loc[df2['Party'] == 'REP', precinct_name].iloc[0]
            self.shape_data.loc[ind, 'pct_repub'] = totalRepVotes / (totalDemVotes+totalRepVotes) * 100
        self.shape_data[['PlaceNam', 'PrecNum', 'pct_repub']].to_csv(f'voting_data_{contest}_{self.year}.csv')

    def plot_data(self, contest):
        # data = gpd.read_file(shapefile)
        # pollingLocData = gpd.read_file(pollingLocFile)
        # data = shapefile.loc[shapefile['COUNTYFP20']=='089']
        # df = pd.read_excel(resultsfile)
        self.df1.loc[:, 'Contest Title'] = self.df1['Contest Title'].apply(lambda x: x.strip())


        fig = px.choropleth_map(self.shape_data, geojson=self.shape_data['geometry'], locations=self.shape_data.index, color='pct_repub',
                                   color_continuous_scale="Bluered",
                                   range_color=(0, 100),
                                   labels={'pct_repub': 'Percentage Republican'},
                                   hover_name='PlaceNam',
                                   map_style="open-street-map",
                                    # map_style="carto-positron",
                                   center=dict(lat=34.74914, lon=-86.57546),
                                   zoom=10,
                                   # opacity=0.4,
                                   title='2026 Primary Results',
                                   )
        fig.update_traces(marker_line_width=0, marker_opacity=0.6)
        fig.update_geos(
            showsubunits=True, subunitcolor="black"
        )

        fig.add_scattermap(
            lat=list(self.shape_data['geometry'].centroid.y),
            lon=list(self.shape_data['geometry'].centroid.x),
            text=list(self.shape_data['PrecNum'].astype(int)),
            mode='text',
            hoverinfo='skip',
            textfont={'color': 'black'},
        )
        fig.add_scattermap(
            lat=[35.0],
            lon=[-86.57546],
            text=[contest + " Results"],
            mode='text',
            hoverinfo='skip',
            textfont={'color': 'black'},
        )
        fig.update_layout(
            height=1000,
            autosize=True,
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            paper_bgcolor="#303030",
            plot_bgcolor="#303030",
            map_layers=[
                {
                    "below": "traces",
                    "sourcetype": "raster",
                    "sourceattribution": "© OpenStreetMap contributors",
                    "source": [
                        "https://openstreetmap.org{z}/{x}/{y}.png"
                    ]
                }]
        )

        fig.show()
        fig.write_html(f'../pages/Precinct_Voting_Map_{contest.replace(' ', '_')}_{self.year}.html')

if __name__ == "__main__":
    year = 2026
    polling_location_file = '../data/precinct-numbers/2026-Polling-Locations-Madison-County-.pdf'
    results_file = '../data/madison-county-votes/2026_GENERAL_ELECTION-MADISON.xls'
    shapefile_path = '../data/shapefiles/precincts_2026_rev2.shp'
    pollingData = PollingData(year, polling_location_file, results_file, shapefile_path)
    pollingData.match_polling_places()
    pollingData.determine_dem_rep_pct('GOVERNOR', False)
    pollingData.plot_data('Governor')

    pollingData.determine_dem_rep_pct('UNITED STATES SENATOR', False)
    pollingData.plot_data('Senator')

    pollingData.determine_dem_rep_pct('ATTORNEY GENERAL', False)
    pollingData.plot_data('Attorny General')

    pollingData.determine_dem_rep_pct('UNITED STATES REPRESENTATIVE, 5TH CONGRESSIONAL DISTRICT', False)
    pollingData.plot_data('5th Congressional District Representative')
