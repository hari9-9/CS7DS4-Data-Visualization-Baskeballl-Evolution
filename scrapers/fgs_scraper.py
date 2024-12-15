from nba_api.stats.endpoints import shotchartdetail
import pandas as pd
import time

# Function to fetch field goal attempts data for a given season
def fetch_attempted_data(season):
    """
    Fetch total field goals attempted (2-pointers and 3-pointers) for a given NBA season.

    Parameters:
        season (str): The season to fetch data for, e.g., '2022-23'.

    Returns:
        dict: A dictionary containing the total 2-pointers and 3-pointers attempted for the season.
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

        # Filter data for 2-pointers and 3-pointers
        shot_data['SHOT_TYPE'] = shot_data['SHOT_TYPE'].apply(lambda x: '3PT' if '3PT' in x else '2PT')

        # Count attempts for 2-pointers and 3-pointers
        attempts = shot_data.groupby('SHOT_TYPE').size()
        two_point_attempts = attempts.get('2PT', 0)
        three_point_attempts = attempts.get('3PT', 0)

        return {
            'season': season,
            '2pts_attempted': two_point_attempts,
            '3pts_attempted': three_point_attempts
        }

    except Exception as e:
        print(f"An error occurred while fetching data for season {season}: {e}")
        return {
            'season': season,
            '2pts_attempted': 0,
            '3pts_attempted': 0
        }

# Loop over the seasons and compile data
start_year = 2008
end_year = 2024
field_goal_attempts = []

for year in range(start_year, end_year + 1):
    season = f"{year}-{str(year + 1)[-2:]}"
    season_data = fetch_attempted_data(season)
    field_goal_attempts.append(season_data)

    # Respectful delay to avoid rate-limiting
    time.sleep(1)

# Convert the results to a DataFrame
attempts_df = pd.DataFrame(field_goal_attempts)

# Save the results to a CSV file
output_file = 'field_goal_attempts_by_season.csv'
attempts_df.to_csv(output_file, index=False)
print(f"Data saved to {output_file}")
