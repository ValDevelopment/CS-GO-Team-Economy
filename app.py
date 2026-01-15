import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import matplotlib.pyplot as plt
import os
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Counter Strike Team Economy Analysis", layout="wide")
st.title("Counter Strike Team Economy Analysis")

st.markdown(
    """
    This app analyzes **round-by-round economic decisions in Counter-Strike matches**.
    
    Select a matchup and map to examine team investments each round, 
    how economies evolve throughout the game, and how spending relates to round outcomes.
    """
)


DATA_PATH = Path(__file__).parent / "data" / "raw"/ "econ_results_merged.csv"


@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

df = load_data(DATA_PATH)

#st.write(f"Loaded shape: {df.shape[0]} rows × {df.shape[1]} columns")
#st.dataframe(df.head(n))

def plot_round_investment(econ_results_merged, match_id, map_number):
    # Filter to match
    df_match = econ_results_merged.query("match_id == @match_id").copy()
    if df_match.empty:
        st.warning("No rows found for that match_id.")
        return

    df_map = df_match.query("_map == @map_number").copy()
    if df_map.empty:
        st.warning("No rows found for that map number for this match.")
        return

    row = df_map.iloc[0]

    t1_cols = [f"{i}_t1" for i in range(1, 31)]
    t2_cols = [f"{i}_t2" for i in range(1, 31)]
    winner_cols = [f"{i}_winner" for i in range(1, 31)]

    t1_econ = row[t1_cols].dropna()
    t2_econ = row[t2_cols].dropna()
    winners = row[winner_cols].dropna()

    t1_econ.index = t1_econ.index.str.replace("_t1", "", regex=False)
    t2_econ.index = t2_econ.index.str.replace("_t2", "", regex=False)
    winners.index = winners.index.str.replace("_winner", "", regex=False)

    n_rounds = len(t1_econ)
    if n_rounds == 0:
        st.warning("No round investment data found for this match/map.")
        return

    x = np.arange(n_rounds) * 1.5

    team1 = row.get("team_1_x", "Team 1")
    team2 = row.get("team_2_x", "Team 2")

    fig, ax = plt.subplots(figsize=(10, 4))

    ax.bar(
        x - 0.25, t1_econ.iloc[:n_rounds], width=0.5, alpha=0.9,
        edgecolor="black", linewidth=0.3, label=team1
    )
    ax.bar(
        x + 0.25, t2_econ.iloc[:n_rounds], width=0.5, alpha=0.9,
        edgecolor="black", linewidth=0.3, label=team2
    )

    ax.set_xticks(x)
    ax.set_xticklabels([str(i) for i in range(1, n_rounds + 1)])
    ax.set_xlabel("Round")
    ax.set_ylabel("$ Invested")
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.margins(y=0.06)

    for i in range(n_rounds):
        winner_val = row.get(f"{i+1}_winner", np.nan)

        if winner_val == 1:
            ax.text(x[i] - 0.25, float(t1_econ.iloc[i]) + 500, "★",
                    ha="center", va="bottom")
        elif winner_val == 2:
            ax.text(x[i] + 0.25, float(t2_econ.iloc[i]) + 500, "★",
                    ha="center", va="bottom")

    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5), frameon=False)
    fig.tight_layout()

    st.pyplot(fig)

@st.cache_data(show_spinner=False)
def get_row_for_match_map(df, match_id, map_number):
    df_map = df.query("match_id == @match_id and _map == @map_number")
    if df_map.empty:
        return None
    return df_map.iloc[0]

def plot_team_line(row, team_side: int):
    """
    team_side: 1 or 2
    Plots a single team's econ line with ★ for won rounds, X for lost rounds.
    """
    econ_cols = [f"{i}_t{team_side}" for i in range(1, 31)]
    econ = row[econ_cols].dropna()

    econ.index = econ.index.str.replace(f"_t{team_side}", "", regex=False)

    n_rounds = len(econ)
    if n_rounds == 0:
        st.warning("No round econ data found.")
        return

    team_name = row.get("team_1_x" if team_side == 1 else "team_2_x", f"Team {team_side}")

    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(range(1, n_rounds + 1), econ.values)

    ax.set_xlabel("Round")
    ax.set_ylabel("$ Invested")
    ax.set_title(team_name)

    for i in range(n_rounds):
        winner_val = row.get(f"{i+1}_winner", np.nan)
        y = float(econ.iloc[i])
        x = i + 1

        if (team_side == 1 and winner_val == 1) or (team_side == 2 and winner_val == 2):
            ax.text(x, y, "★", ha="center", va="bottom", color="black")
        elif winner_val in (1, 2):
            ax.text(x, y, "X", ha="center", va="bottom", color="black")

    ax.grid(axis="x", linestyle="--", alpha=1)
    fig.tight_layout()
    st.pyplot(fig)

def plot_econ_heatmap(row):
    t1_cols = [f"{i}_t1" for i in range(1, 31)]
    t2_cols = [f"{i}_t2" for i in range(1, 31)]

    t1_econ = row[t1_cols].dropna().astype(int).to_numpy()
    t2_econ = row[t2_cols].dropna().astype(int).to_numpy()

    n_rounds = min(len(t1_econ), len(t2_econ))
    if n_rounds == 0:
        st.warning("No round econ data found.")
        return

    econ_data = np.vstack([t1_econ[:n_rounds], t2_econ[:n_rounds]])

    t1_rounds, t2_rounds = [], []
    for i in range(n_rounds):
        winner_val = row.get(f"{i+1}_winner", np.nan)
        if winner_val == 1:
            t1_rounds.append("W"); t2_rounds.append("L")
        elif winner_val == 2:
            t1_rounds.append("L"); t2_rounds.append("W")
        else:
            t1_rounds.append("");  t2_rounds.append("")

    winners_text = np.vstack([t1_rounds, t2_rounds])

    team1 = row.get("team_1_x", "Team 1")
    team2 = row.get("team_2_x", "Team 2")

    fig = go.Figure(
        data=go.Heatmap(
            z=econ_data,
            text=winners_text,
            texttemplate="%{text}",
            colorscale="RdYlGn",
            colorbar=dict(title="$ Invested")
        )
    )

    fig.update_layout(
        title="Economy heatmap (W/L annotated)",
        xaxis=dict(
            title="Round",
            tickmode="array",
            tickvals=list(range(n_rounds)),
            ticktext=[str(i) for i in range(1, n_rounds + 1)]
        ),
        yaxis=dict(
            title="Team",
            tickmode="array",
            tickvals=[0, 1],
            ticktext=[team1, team2]
        ),
        height=320,
        margin=dict(l=40, r=20, t=50, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)


@st.cache_data(show_spinner=False)
def build_match_list(df: pd.DataFrame) -> pd.DataFrame:
    base = (
        df.sort_values(["match_id", "_map"])
          .drop_duplicates(subset=["match_id"])
          .copy()
    )

    possible_date_cols = ["date_x", "match_date", "start_date", "datetime", "timestamp"]
    date_col = next((c for c in possible_date_cols if c in base.columns), None)

    keep_cols = ["match_id", "team_1_x", "team_2_x"]
    if date_col:
        keep_cols.insert(0, date_col)

    base = base[keep_cols].copy()

    base["team_1_x"] = base["team_1_x"].fillna("Team 1")
    base["team_2_x"] = base["team_2_x"].fillna("Team 2")

    if date_col:
        dt = pd.to_datetime(base[date_col], errors="coerce")
        base["date_str"] = dt.dt.strftime("%Y-%m-%d")
        base["date_str"] = base["date_str"].fillna("Unknown date")
        base["label"] = (
            base["date_str"] + " — " +
            base["match_id"].astype(str) + " — " +
            base["team_1_x"] + " vs " + base["team_2_x"]
        )
    else:
        base["label"] = (
            base["match_id"].astype(str) + " — " +
            base["team_1_x"] + " vs " + base["team_2_x"]
        )

    return base


match_list = build_match_list(df)


# UI

import shlex
import re
query = st.text_input(
    "Search matchup (e.g., 'Vitality vs Virtus Pro' or 'Vitality Virtus Pro')",
    placeholder="Examples: Vitality vs Virtus Pro | Virtus Pro | \"Virtus Pro\" Vitality |" 
).strip()

q = query.lower()
q = re.sub(r"\bvs\b|\bv\b|,|\||-|/", " vs ", q)
q = re.sub(r"\s+", " ", q).strip()

if " vs " in q:
    parts = [p.strip() for p in q.split(" vs ") if p.strip()]
else:
    parts = shlex.split(q) 

if len(parts) == 0:
    filtered = match_list.head(200).copy()
    st.caption("Type a matchup to search (e.g., 'Vitality vs Optic'). Showing first 200 matches for now.")
elif len(parts) == 1:
    t = parts[0]
    filtered = match_list[
        match_list["team_1_x"].str.lower().str.contains(t, na=False) |
        match_list["team_2_x"].str.lower().str.contains(t, na=False)
    ].copy()
    st.caption(f"Found {len(filtered)} matches containing '{parts[0]}'")
else:
    t1, t2 = parts[0], parts[1]

    team1_lower = match_list["team_1_x"].str.lower()
    team2_lower = match_list["team_2_x"].str.lower()

    filtered = match_list[
        (
            (team1_lower.str.contains(t1, na=False) & team2_lower.str.contains(t2, na=False)) |
            (team1_lower.str.contains(t2, na=False) & team2_lower.str.contains(t1, na=False))
        )
    ].copy()

    st.caption(f"Found {len(filtered)} matches for '{t1}' vs '{t2}'")


selected_label = st.selectbox("Choose a match", filtered["label"].tolist())
match_id = int(filtered.loc[filtered["label"] == selected_label, "match_id"].iloc[0])

df_match = df.query("match_id == @match_id")

if df_match.empty:
    st.info("Enter a match_id that exists in the data.")
else:
    map_options = sorted(df_match["_map"].dropna().unique().tolist())
    map_number = st.selectbox("Map number", map_options)

    view = st.radio(
    "Choose a view",
    ["Barplots (both teams)", "Line graphs (per team)", "Heatmap (W/L)"],
    horizontal=True
)

    if view == "Barplots (both teams)":
        st.subheader("Round investment by team (barplots)")
        st.caption(
            "Shows the amount each team invested per round. "
            "Stars indicate the round winner."
        )
        plot_round_investment(df, match_id, map_number)

    elif view == "Line graphs (per team)":
        st.subheader("Round investment (line graphs)")
        st.caption(
            "Tracks each team’s economy over the course of the map. "
            "Stars indicate rounds won; X marks indicate rounds lost."
        )
        row = get_row_for_match_map(df, match_id, map_number)
        if row is None:
            st.warning("No data for that match/map.")
        else:
            c1, c2 = st.columns(2)
            with c1:
                plot_team_line(row, 1)
            with c2:
                plot_team_line(row, 2)
    elif view == "Heatmap (W/L)":
        st.caption(
            "Each cell represents a team’s investment in a given round. "
            "Green indicates higher spending, red indicates lower spending. "
            "Cells are annotated with W/L to show round outcomes."
        )
        row = get_row_for_match_map(df, match_id, map_number)
        if row is None:
            st.warning("No data for that match/map.")
            
        else:
            plot_econ_heatmap(row)
