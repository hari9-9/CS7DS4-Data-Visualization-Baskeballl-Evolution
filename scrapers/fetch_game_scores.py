from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd
import time

# Function to fetch total points for all games in a season
def fetch_total_points_by_season(season):
    """
    Fetch total points scored in all games for a given NBA season.

    Parameters:
        season (str): The season to fetch data for, e.g., '2022-23'.

    Returns:
        float: The average total points scored per game for the specified season.
    """
    print(f"Fetching game scores for season {season}...")

    try:
        # Fetch game data using leaguegamefinder
        response = leaguegamefinder.LeagueGameFinder(season_nullable=season, season_type_nullable='Regular Season')
        games = response.get_data_frames()[0]

        # Calculate total points per game
        games['TOTAL_POINTS'] = games.groupby('GAME_ID')['PTS'].transform('sum')

        # Remove duplicate entries for each game
        games = games.drop_duplicates(subset=['GAME_ID'])

        # Calculate average points per game
        avg_points = games['TOTAL_POINTS'].mean()
        return {'season': season, 'average_points': avg_points}

    except Exception as e:
        print(f"An error occurred while fetching data for season {season}: {e}")
        return {'season': season, 'average_points': None}

# Loop over the seasons and compile data
start_year = 2008
end_year = 2023
average_points_per_season = []

for year in range(start_year, end_year + 1):
    season = f"{year}-{str(year + 1)[-2:]}"
    season_data = fetch_total_points_by_season(season)
    average_points_per_season.append(season_data)

    # Respectful delay to avoid rate-limiting
    time.sleep(1)

# Convert the results to a DataFrame
average_points_df = pd.DataFrame(average_points_per_season)

# Save the results to a CSV file
output_file = 'average_points_by_season.csv'
average_points_df.to_csv(output_file, index=False)
print(f"Data saved to {output_file}")
