# CS7DS4: Data Visualization – Basketball Evolution Dashboard
This project visualizes the evolution of NBA shooting trends over time, focusing on the rise of the 3-point shot and scoring patterns. The dashboard provides interactive and dynamic visualizations, enabling users to explore shooting data across multiple NBA seasons (2008-09 to 2023-24).

## Features
 - Interactive Shot Chart: Explore 2-point and 3-point shooting locations on a scaled basketball court.
 - Temporal Trends: Line charts showing changes in average points per game and shot attempts (2PT vs. 3PT) over seasons.
 - Hot Zone Analysis: Highlights the top 5 shooting zones outside the layup area for each season.
 - Critical Comparison: Pie charts comparing 4th-quarter shot preferences between the 2008-09 and 2023-24 seasons.
 - Dynamic Exploration: Use sliders and play functionality to navigate through seasons.

## Getting Started
Prerequisites
Ensure you have the following installed:

Python: Version 3.7 or later.
pip: Python's package manager.
```bash
git clone https://github.com/hari9-9/CS7DS4-Data-Visualization-Baskeballl-Evolution.git
cd CS7DS4-Data-Visualization-Baskeballl-Evolution

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

python dashboard.py
```


## Project Overview
This project is part of the CS7DS4 Data Visualization module and highlights the power of visual analytics in understanding trends in basketball shooting strategies. It utilizes:

NBA API for data retrieval.
Matplotlib for advanced visualizations.
Pandas and NumPy for data preprocessing and transformation.
Through dynamic and interactive elements, the dashboard provides insights into the NBA's shifting shooting preferences and scoring dynamics.