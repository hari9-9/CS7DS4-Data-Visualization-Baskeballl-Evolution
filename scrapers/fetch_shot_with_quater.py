from nba_api.stats.endpoints import shotchartdetail
import pandas as pd
import time

# Function to fetch and save shot data for a given season
def fetch_shot_data(season):
    """
    Fetch all made shots (x and y coordinates) for a given NBA season.
    Additionally, determine if each shot was a 2-pointer or 3-pointer and the quarter it was taken.

    Parameters:
        season (str): The season to fetch data for, e.g., '2022-23'.

    Returns:
        DataFrame: Data of made shots for the specified season.
    """
    print(f"Fetching shot data for season {season}...")

    try:
        # Fetch shot chart details
        response = shotchartdetail.ShotChartDetail(
            team_id=0,  # Fetch data for all teams
            player_id=0,  # Fetch data for all players
            season_nullable=season,
            season_type_all_star='Regular Season'
        )

        # Extract shot chart data
        shot_data = response.get_data_frames()[0]

        # Filter for made shots
        made_shots = shot_data[shot_data['SHOT_MADE_FLAG'] == 1]

        # Determine if the shot was a 2-pointer or 3-pointer
        made_shots['SHOT_TYPE'] = made_shots['SHOT_TYPE'].apply(lambda x: '3PT' if '3PT' in x else '2PT')

        # Add a column for the season
        made_shots['SEASON'] = season

        # Select relevant columns including quarter (PERIOD)
        made_shots = made_shots[['LOC_X', 'LOC_Y', 'SHOT_TYPE', 'GAME_ID', 'GAME_DATE', 'PERIOD', 'SEASON']]

        return made_shots

    except Exception as e:
        print(f"An error occurred while fetching data for season {season}: {e}")
        return None

# Loop over the last 15 seasons and compile all data into one DataFrame
start_year = 2008
end_year = 2023
all_data = []

for year in range(start_year, end_year + 1):
    season = f"{year}-{str(year + 1)[-2:]}"
    season_data = fetch_shot_data(season)
    if season_data is not None:
        all_data.append(season_data)

    # Respectful delay to avoid rate-limiting
    time.sleep(1)

# Combine all data into a single DataFrame
final_data = pd.concat(all_data, ignore_index=True)

# Save to a single CSV file
final_data.to_csv('all_made_shots_with_quater.csv', index=False)
print("All data saved to 'all_made_shots.csv'")
