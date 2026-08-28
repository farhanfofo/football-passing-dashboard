import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsbombpy import sb
from mplsoccer import Pitch

st.set_page_config(page_title="Football Analytics Dashboard", layout="wide")
st.title("⚽ Football Passing Dashboard")

# Sidebar Filters
st.sidebar.header("Configuration")

# Dynamic Competition & Match Selection
competitions = sb.competitions()
selected_comp_name = st.sidebar.selectbox("Competition", competitions["competition_name"].unique())

comp_row = competitions[competitions["competition_name"] == selected_comp_name]
competition_id = comp_row["competition_id"].values[0]
season_id = comp_row["season_id"].values[0]

matches = sb.matches(competition_id=competition_id, season_id=season_id)
match_options = {f"{row['home_team']} vs {row['away_team']} ({row['match_date']})": row['match_id'] for index, row in matches.iterrows()}

selected_match_label = st.sidebar.selectbox("Select Match", list(match_options.keys()))
match_id = match_options[selected_match_label]

team_name = st.sidebar.text_input("Enter Team Name", value="Argentina")

@st.cache_data
def load_data(m_id):
    return sb.events(match_id=m_id)

try:
    events = load_data(match_id)
    team_events = events[events["team"] == team_name]

    players = team_events["player"].dropna().unique()
    selected_player = st.sidebar.selectbox("Select Player", players)

    player_passes = team_events[
        (team_events["player"] == selected_player) & 
        (team_events["type"] == "Pass") & 
        (team_events["pass_outcome"].isna())
    ].copy()

    player_passes["x_start"] = player_passes["location"].apply(lambda loc: loc[0])
    player_passes["y_start"] = player_passes["location"].apply(lambda loc: loc[1])
    player_passes["x_end"] = player_passes["pass_end_location"].apply(lambda loc: loc[0])
    player_passes["y_end"] = player_passes["pass_end_location"].apply(lambda loc: loc[1])

    st.markdown(f"### Pass Map: **{selected_player}**")
    st.markdown(f"**Completed Passes:** `{len(player_passes)}` | **Total Match Events:** `{len(team_events[team_events['player'] == selected_player])}`")

    pitch = Pitch(pitch_type='statsbomb', pitch_color='#101010', line_color='#c7d5cc')
    fig, ax = pitch.draw(figsize=(10, 6))
    fig.set_facecolor('#101010')

    pitch.arrows(
        player_passes["x_start"], player_passes["y_start"],
        player_passes["x_end"], player_passes["y_end"],
        width=2, headwidth=4, color="#00BFFF", alpha=0.8, ax=ax
    )
    pitch.scatter(
        player_passes["x_start"], player_passes["y_start"],
        s=40, color="#FFD700", edgecolors="#ffffff", ax=ax, zorder=3
    )

    st.pyplot(fig)

except Exception as e:
    st.error(f"Error loading match data: {e}")
    
