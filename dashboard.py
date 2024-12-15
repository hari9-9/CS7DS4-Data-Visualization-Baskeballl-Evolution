import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
from matplotlib.widgets import Slider, Button
from matplotlib.gridspec import GridSpec
import numpy as np

# Function to draw the basketball court
def draw_court(ax=None, color="black", lw=3):
    """
    Draw a basketball half-court using Matplotlib.
    """
    if ax is None:
        ax = plt.gca()

    # Create the basketball hoop
    hoop = Circle((0, 5.25), radius=0.75, linewidth=lw, color=color, fill=False)

    # Create the backboard
    backboard = Rectangle((-3, 4), 6, 0.5, linewidth=lw, color=color, fill=False)

    # Create the paint area (key)
    outer_box = Rectangle((-8, 0), 16, 19, linewidth=lw, color=color, fill=False)
    inner_box = Rectangle((-6, 0), 12, 19, linewidth=lw, color=color, fill=False)

    # Free throw circle
    free_throw_circle = Arc((0, 19), 12, 12, theta1=0, theta2=180, linewidth=lw, color=color)

    # Restricted area
    restricted_arc = Arc((0, 5.25), 8, 8, theta1=0, theta2=180, linewidth=lw, color=color)

    # Three-point line
    three_point_arc = Arc((0, 5.25), 47.5, 47.5, theta1=22, theta2=158, linewidth=lw, color=color)
    three_point_line_left = Rectangle((-22, 0), 0, 14, linewidth=lw, color=color, fill=False)
    three_point_line_right = Rectangle((22, 0), 0, 14, linewidth=lw, color=color, fill=False)

    # Add elements to the plot
    ax.add_patch(hoop)
    ax.add_patch(backboard)
    ax.add_patch(outer_box)
    ax.add_patch(inner_box)
    ax.add_patch(free_throw_circle)
    ax.add_patch(restricted_arc)
    ax.add_patch(three_point_arc)
    ax.add_patch(three_point_line_left)
    ax.add_patch(three_point_line_right)

    # Set the limits and aspect ratio
    ax.set_xlim(-25, 25)
    ax.set_ylim(0, 47)
    ax.set_aspect("equal")

# Load the combined dataset for shots
shot_data = pd.read_csv('all_made_shots_with_quater.csv')
shot_data['PLOT_X'] = shot_data['LOC_X'] / 250 * 25  # Scale to court width (-25 to 25 feet)
shot_data['PLOT_Y'] = (shot_data['LOC_Y'] / 422 * 47) + 2  # Scale to court length (0 to 47 feet)

# Group data by season and sample 10% from each season
shot_data_dict = {season: df.sample(frac=0.1, random_state=42) for season, df in shot_data.groupby('SEASON')}

# Load field goal attempts data
attempt_data = pd.read_csv('field_goal_attempts_by_season.csv')

# Load average points data
average_points_data = pd.read_csv('average_points_by_season.csv')
average_points_data['average_points'] = average_points_data['average_points'].round().astype(int)

# Create the dashboard layout
fig = plt.figure(figsize=(20, 16))
gs = GridSpec(3, 3, width_ratios=[3, 1.5, 1], height_ratios=[4, 2, 1.5], figure=fig)

# Create the shooting chart on the left
ax_shot_chart = fig.add_subplot(gs[:, 0])
draw_court(ax_shot_chart)
scatter_2pt = ax_shot_chart.scatter([], [], c='green', alpha=0.3, label='2PT Shots')
scatter_3pt = ax_shot_chart.scatter([], [], c='blue', alpha=0.3, marker='^' , label='3PT Shots')
title_text = ax_shot_chart.text(0.5, 1.05, "", transform=ax_shot_chart.transAxes, ha="center", fontsize=24, weight='bold')
ax_shot_chart.set_ylabel("Court Length (feet)")
ax_shot_chart.set_xlabel("Scaled Down Basketball Court")
ax_shot_chart.set_xticks([])
ax_shot_chart.legend()

# Slider for year selection
ax_slider = plt.axes([0.05, 0.02, 0.4, 0.03])  # Slider confined to the left half
years = list(shot_data_dict.keys())

# Create a slider with valfmt for displaying the year
slider = Slider(
    ax_slider,
    'Year',
    0,
    len(years) - 1,
    valinit=0,
    valstep=1,
    valfmt='%s'  # Display year strings
)

# Define the layup zone (circular area around the rim)
layup_radius = 5.0  # Radius of layup area (in feet)
layup_center = (0, 5.25)  # Center of the rim

# Filter out layup shots from the dataset
def is_outside_layup_zone(x, y):
    """Check if a shot is outside the layup zone."""
    return (x - layup_center[0])**2 + (y - layup_center[1])**2 > layup_radius**2

shot_data['OUTSIDE_LAYUP_ZONE'] = shot_data.apply(lambda row: is_outside_layup_zone(row['PLOT_X'], row['PLOT_Y']), axis=1)

# Divide the court into grid
num_bins_x = 16  # resolution for width
num_bins_y = 16  # resolution for length
x_edges = pd.cut(shot_data['PLOT_X'], bins=num_bins_x, labels=False, retbins=True)[1]
y_edges = pd.cut(shot_data['PLOT_Y'], bins=num_bins_y, labels=False, retbins=True)[1]

# Precompute shot densities excluding the layup zone for each year and grid cell
hot_zone_data = {}
for season, df in shot_data[shot_data['OUTSIDE_LAYUP_ZONE']].groupby('SEASON'):
    heatmap, _, _ = np.histogram2d(df['PLOT_X'], df['PLOT_Y'], bins=[x_edges, y_edges])
    hot_zone_data[season] = heatmap

# Add a patch container for hot zones
hot_zone_patches = []

def update_hot_zones(season):
    """
    Update hot zones for a given season by highlighting the top 5 shooting areas outside the layup zone.
    """
    # Clear existing hot zones
    global hot_zone_patches
    for patch in hot_zone_patches:
        patch.remove()
    hot_zone_patches = []

    # Get the heatmap for the current season
    heatmap = hot_zone_data[season]
    flat_heatmap = heatmap.flatten()
    top_indices = np.argsort(flat_heatmap)[-5:]  # Get indices of top 5 density cells
    top_indices = np.unravel_index(top_indices, heatmap.shape)  # Convert to 2D indices

    for x_idx, y_idx in zip(*top_indices):
        # Calculate the coordinates of the grid cell
        x_min = x_edges[x_idx]
        x_max = x_edges[x_idx + 1]
        y_min = y_edges[y_idx]
        y_max = y_edges[y_idx + 1]

        # Add a transparent rectangle for the hot zone
        rect = Rectangle(
            (x_min, y_min),  # Bottom-left corner
            x_max - x_min,  # Width
            y_max - y_min,  # Height
            color='red',
            alpha=0.3,
            edgecolor='red',
            linewidth=1.5
        )
        hot_zone_patches.append(rect)
        ax_shot_chart.add_patch(rect)

# Update function for the slider
def update(val):
    year_index = int(slider.val)
    year = years[year_index]
    current_data = shot_data_dict[year]
    scatter_2pt.set_offsets(current_data[current_data['SHOT_TYPE'] == '2PT'][['PLOT_X', 'PLOT_Y']].values)
    scatter_3pt.set_offsets(current_data[current_data['SHOT_TYPE'] == '3PT'][['PLOT_X', 'PLOT_Y']].values)
    ax_shot_chart.set_title(f"NBA Shooting Trends: 2 PTS vs 3 PTS ({year})", fontsize=16)
    update_hot_zones(year)
    fig.canvas.draw_idle()

slider.on_changed(update)


# Play button
ax_play = plt.axes([0.5, 0.02, 0.08, 0.04])  # Play button near the slider
button = Button(ax_play, 'Play')

# Flag to track playing state
playing = False

# Play/Pause function for the button
def toggle_play(event):
    global playing
    playing = not playing  # Toggle the playing state
    button.label.set_text('Stop' if playing else 'Play')  # Update button label

    if playing:
        for year_index in range(len(years)):
            if not playing:  # Stop animation if "Pause" is clicked
                break
            slider.set_val(year_index)
            plt.pause(0.5)  # Pause for half a second to create transition effect

button.on_clicked(toggle_play)


# Create the line chart for field goal attempts (top-right)
ax_line_chart = fig.add_subplot(gs[0, 1:])
x_ticks = range(0, len(attempt_data), max(1, len(attempt_data) // 5))
ax_line_chart.plot(attempt_data['season'], attempt_data['2pts_attempted'], label='2PT Attempts', color='green')
ax_line_chart.plot(attempt_data['season'], attempt_data['3pts_attempted'], label='3PT Attempts', color='blue')
ax_line_chart.set_title("Tracking the Rise of the Three point shot: Total Attempts Through the Years", fontsize=16)
ax_line_chart.set_xlabel("Season")
ax_line_chart.set_ylabel("Attempts")
ax_line_chart.set_xticks(x_ticks)
ax_line_chart.set_xticklabels([attempt_data['season'][i] for i in x_ticks], rotation=45)
ax_line_chart.legend()

# Create the line chart for average points (middle-right)
ax_avg_points = fig.add_subplot(gs[1, 1:])
ax_avg_points.plot(average_points_data['season'], average_points_data['average_points'], label='Avg Points', color='orange')
ax_avg_points.set_title("Rise in Average Points per Game Over the Years", fontsize=16)
ax_avg_points.set_xlabel("Season")
ax_avg_points.set_ylabel("Avg Points")
x_ticks_avg = range(0, len(average_points_data), max(1, len(average_points_data) // 5))
ax_avg_points.set_xticks(x_ticks_avg)
ax_avg_points.set_xticklabels([average_points_data['season'][i] for i in x_ticks_avg], rotation=45)
ax_avg_points.legend()

# Add two pie charts for period 4 comparison (bottom-right split)
ax_pie_2008 = fig.add_subplot(gs[2, 1])
ax_pie_2023 = fig.add_subplot(gs[2, 2])

# Prepare data for pie charts
comparison_data = shot_data[(shot_data['PERIOD'] == 4) & (shot_data['SEASON'].isin(['2008-09', '2023-24']))]
comparison_data_2008 = comparison_data[comparison_data['SEASON'] == '2008-09']['SHOT_TYPE'].value_counts()
comparison_data_2023 = comparison_data[comparison_data['SEASON'] == '2023-24']['SHOT_TYPE'].value_counts()

# Labels and colors for the legends
labels = comparison_data_2008.index
colors = ['green', 'blue']

# Plot pie chart for 2008-09
ax_pie_2008.pie(
    comparison_data_2008,
    labels=None,  # Avoid duplicate labels in both chart and legend
    autopct='%1.1f%%',
    startangle=90,
    colors=colors,
    textprops={'color': 'white'}
)
ax_pie_2008.set_title("Back in 2008")


# Plot pie chart for 2023-24
ax_pie_2023.pie(
    comparison_data_2023,
    labels=None,  # Avoid duplicate labels in both chart and legend
    autopct='%1.1f%%',
    startangle=90,
    colors=colors,
    textprops={'color': 'white'}
)
ax_pie_2023.set_title("Currently in 2024")
ax_pie_2023.legend(
    labels,  # Use the same labels
    loc="upper left",
    bbox_to_anchor=(0.1, -0.1),  # Adjust legend position if needed
    fontsize=10
)

# Add text below the pie charts
fig.text(
    0.77,  # X-coordinate (adjust as needed for horizontal placement)
    0.05,  # Y-coordinate (adjust as needed for vertical placement)
    "What did the Shooters Prefer with the \n Game on the line?(4th Quater)",  # Text content
    ha='center',
    fontsize=12,
    fontweight='bold'
)

# Add a title to the top of the dashboard
fig.suptitle(
    "The 3-Point Revolution in Basketball: A Visual Journey Through the NBA's Shot Evolution",  # Title text
    fontsize=20,
    fontweight='bold',  # Make the text bold
    y=0.95
)
# Add a legend entry for the red hot zones
hot_zone_legend = Rectangle((0, 0), 1, 1, color='red', alpha=0.3, label='Top 5 Shooting Zones\n(excluding under the basket)')
# Add a combined legend
handles, labels = ax_shot_chart.get_legend_handles_labels()  # Get existing legend entries
handles.append(hot_zone_legend)  # Add the hot zone legend
labels.append('Top 5 Shooting Zones\n(excluding layups)')  # Add label for the hot zone legend

ax_shot_chart.legend(
    handles=handles,
    loc='upper right',
    fontsize=10,
    frameon=True,
    title="Legend"
)
# Add descriptive text to the shot chart area
fig.text(
    0.08,
    0.89,
    "Info:\n"
    "2PT: 2-pointer shots taken within the three-point arc, closer to the basket.\n"
    "3PT: 3-pointer shots taken beyond the three-point arc",
    fontsize=10,
    ha='left',
    va='center',
    color='black',
    style='italic'
)

# Adjust layout and spacing
plt.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.1, wspace=0.4, hspace=0.6)
update(0)
plt.show()
