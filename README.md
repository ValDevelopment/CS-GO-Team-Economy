# CS:GO Round Economy Analysis

Interactive tool for exploring round-by-round economic decisions in professional CS:GO matches (11/2015 to 03/2020).

**[Live app](https://counter-strike-analytics.streamlit.app/)**

## Overview

This app analyzes 25K+ professional CS:GO matches from a public dataset of round-by-round economic data (per-team investment and round winner, for every round of every map). It's built as a Streamlit app for browsing any matchup and seeing exactly how each team managed its economy round by round, giving teams and analysts a way to study opponents' spending tendencies (buy timing, force buys, eco patterns) without watching full VODs.

## Features

- **Matchup search**: type any team names or match ID to pull up historical matches instantly
- **Barplots**: side-by-side per-round spending comparison, with round winners marked
- **Line graphs**: each team's economy trajectory across a map, wins and losses annotated
- **Heatmap**: full-map investment intensity colored by spend, annotated W/L

## Repo Structure

```
├── data/raw/              # Merged round-by-round economy and match results data
├── notebooks/             # Data cleaning and exploration
├── app.py                 # Streamlit app: search, filtering, and all three visualizations
├── requirements.txt
└── README.md
```

- **`app.py`** is the full app: data loading, matchup search and filtering, and the three visualization functions.
- **`notebooks/`** holds the data cleaning and exploratory work behind `econ_results_merged.csv`.

## Methods

| View | Approach |
|---|---|
| Barplots | Side-by-side bar chart of $ invested per round per team, annotated with round winner |
| Line graphs | Per-team economy line across all rounds in the map, marked W/L per round |
| Heatmap | Round x team investment matrix, colored by spend, annotated W/L |

## Tools

Python · `pandas` / `numpy` (data wrangling) · `streamlit` (app and UI) · `matplotlib` (bar and line plots) · `plotly` (heatmap)

## Reproducing

1. Clone the repo and place `econ_results_merged.csv` in `data/raw/`.
2. Install required packages: `pip install -r requirements.txt`
3. Run the app: `streamlit run app.py`

## Note on data

Underlying data is from the public [CS:GO Professional Matches](https://www.kaggle.com/datasets/mateusdmachado/csgo-professional-matches) dataset on Kaggle (mateusdmachado), covering matches from 11/2015 to 03/2020. It predates CS2, but the schema (round-by-round economy, match results) mirrors what's collectible from CS2 today, so the pipeline is directly reusable with fresh data.
