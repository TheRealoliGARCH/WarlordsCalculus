# ============================================================
# WAR SIMULATION DASHBOARD
# ============================================================
# Author: Lord Soumadeep Ghosh with ChatGPT (OpenAI)
# Framework: Streamlit
#
# Install:
#   pip install streamlit pandas numpy plotly
#
# Run:
#   streamlit run war_dashboard.py
# ============================================================

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import random
from itertools import product

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="War Simulation Dashboard",
    layout="wide",
)

st.title("⚔️ War Simulation Dashboard")
st.caption("Strength Transfer Warfare Model")

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Scenario Setup")

A = st.sidebar.number_input("Attackers (A)", 1, 20, 4)
D = st.sidebar.number_input("Defenders (D)", 1, 20, 4)
N = st.sidebar.number_input("Neutrals (N)", 0, 20, 3)

alpha = st.sidebar.slider(
    "Power Exponent (α)",
    0.1,
    5.0,
    1.0,
    0.1
)

draw_prob = st.sidebar.slider(
    "Draw Probability (δ)",
    0.0,
    1.0,
    0.10,
    0.01
)

battle_order = st.sidebar.selectbox(
    "Battle Order",
    ["Sequential", "Random Shuffle"]
)

st.sidebar.header("Initial Strengths")

attackers = {}
defenders = {}
neutrals = {}

for i in range(A):
    attackers[f"A{i+1}"] = st.sidebar.number_input(
        f"A{i+1}",
        1,
        10000,
        100 - i * 20
    )

for j in range(D):
    defenders[f"D{j+1}"] = st.sidebar.number_input(
        f"D{j+1}",
        1,
        10000,
        90 - j * 20
    )

for k in range(N):
    neutrals[f"N{k+1}"] = st.sidebar.number_input(
        f"N{k+1}",
        1,
        10000,
        50 - k * 10
    )

# ============================================================
# INITIAL TOTALS
# ============================================================

initial_attack_strength = sum(attackers.values())
initial_defense_strength = sum(defenders.values())
neutral_strength = sum(neutrals.values())

total_strength = (
    initial_attack_strength
    + initial_defense_strength
    + neutral_strength
)

combat_strength = (
    initial_attack_strength
    + initial_defense_strength
)

victory_threshold = (
    (np.e - 1) / np.e
) * initial_attack_strength

# ============================================================
# BATTLE MODEL
# ============================================================

def battle_probability(a, d, alpha=1.0, delta=0.1):
    p_draw = delta

    p_attacker = (
        (1 - delta)
        * (a ** alpha)
        / (a ** alpha + d ** alpha)
    )

    p_defender = (
        (1 - delta)
        * (d ** alpha)
        / (a ** alpha + d ** alpha)
    )

    return p_attacker, p_draw, p_defender


def run_simulation():

    atk = attackers.copy()
    dfn = defenders.copy()

    history = []

    attacker_history = [sum(atk.values())]
    defender_history = [sum(dfn.values())]

    battle_matrix = pd.DataFrame(
        0,
        index=list(atk.keys()),
        columns=list(dfn.keys())
    )

    battles = list(product(atk.keys(), dfn.keys()))

    if battle_order == "Random Shuffle":
        random.shuffle(battles)

    for idx, (a_name, d_name) in enumerate(battles):

        a_strength = atk[a_name]
        d_strength = dfn[d_name]

        # Skip dead nations
        if a_strength <= 0 or d_strength <= 0:
            continue

        pA, p0, pD = battle_probability(
            a_strength,
            d_strength,
            alpha,
            draw_prob
        )

        outcome = random.choices(
            [1, 0, -1],
            weights=[pA, p0, pD],
            k=1
        )[0]

        # ----------------------------------------------------
        # ATTACKER WINS
        # ----------------------------------------------------
        if outcome == 1:

            transferred = d_strength

            atk[a_name] += d_strength
            dfn[d_name] = 0

            winner = a_name

        # ----------------------------------------------------
        # DRAW
        # ----------------------------------------------------
        elif outcome == 0:

            transferred = 0
            winner = "Draw"

        # ----------------------------------------------------
        # DEFENDER WINS
        # ----------------------------------------------------
        else:

            transferred = a_strength

            dfn[d_name] += a_strength
            atk[a_name] = 0

            winner = d_name

        battle_matrix.loc[a_name, d_name] = outcome

        attacker_history.append(sum(atk.values()))
        defender_history.append(sum(dfn.values()))

        history.append({
            "Battle": idx + 1,
            "Attacker": a_name,
            "Defender": d_name,
            "Outcome": outcome,
            "Winner": winner,
            "Transferred": transferred,
            "Attacker Total": sum(atk.values()),
            "Defender Total": sum(dfn.values())
        })

    return (
        atk,
        dfn,
        history,
        attacker_history,
        defender_history,
        battle_matrix
    )

# ============================================================
# RUN BUTTON
# ============================================================

if st.button("▶ Run Simulation"):

    (
        final_attackers,
        final_defenders,
        battle_log,
        atk_hist,
        def_hist,
        battle_matrix
    ) = run_simulation()

    final_attack_strength = sum(final_attackers.values())
    final_defense_strength = sum(final_defenders.values())

    attacker_wins = (
        final_attack_strength >= victory_threshold
    )

    # ========================================================
    # TOP METRICS
    # ========================================================

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Total Nations",
        A + D + N
    )

    col2.metric(
        "Total Strength",
        round(total_strength, 2)
    )

    col3.metric(
        "Combat Strength",
        round(combat_strength, 2)
    )

    col4.metric(
        "Victory Threshold",
        round(victory_threshold, 2)
    )

    col5.metric(
        "Projected Winner",
        "ATTACKERS" if attacker_wins else "DEFENDERS"
    )

    st.divider()

    # ========================================================
    # CHARTS
    # ========================================================

    c1, c2 = st.columns([2, 1])

    # --------------------------------------------------------
    # STRENGTH EVOLUTION
    # --------------------------------------------------------

    with c1:

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                y=atk_hist,
                mode='lines+markers',
                name='Attackers'
            )
        )

        fig.add_trace(
            go.Scatter(
                y=def_hist,
                mode='lines+markers',
                name='Defenders'
            )
        )

        fig.add_hline(
            y=victory_threshold,
            line_dash="dash",
            annotation_text="Victory Threshold"
        )

        fig.update_layout(
            title="Strength Evolution",
            xaxis_title="Battle Number",
            yaxis_title="Strength",
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # --------------------------------------------------------
    # CURRENT DISTRIBUTION
    # --------------------------------------------------------

    with c2:

        dist_df = pd.DataFrame({
            "Nation": (
                list(final_attackers.keys())
                + list(final_defenders.keys())
            ),
            "Strength": (
                list(final_attackers.values())
                + list(final_defenders.values())
            ),
            "Side": (
                ["Attackers"] * len(final_attackers)
                + ["Defenders"] * len(final_defenders)
            )
        })

        bar = go.Figure()

        for side in ["Attackers", "Defenders"]:

            sub = dist_df[dist_df["Side"] == side]

            bar.add_trace(
                go.Bar(
                    x=sub["Nation"],
                    y=sub["Strength"],
                    name=side
                )
            )

        bar.update_layout(
            title="Current Strength Distribution",
            barmode="group",
            height=500
        )

        st.plotly_chart(
            bar,
            use_container_width=True
        )

    # ========================================================
    # BATTLE MATRIX
    # ========================================================

    st.subheader("Battle Outcome Matrix")

    st.dataframe(
        battle_matrix,
        use_container_width=True
    )

    # ========================================================
    # BATTLE LOG
    # ========================================================

    st.subheader("Battle Log")

    battle_df = pd.DataFrame(battle_log)

    st.dataframe(
        battle_df,
        use_container_width=True
    )

    # ========================================================
    # FINAL STATUS
    # ========================================================

    st.subheader("War Status")

    s1, s2, s3 = st.columns(3)

    s1.metric(
        "Final Attacker Strength",
        round(final_attack_strength, 2)
    )

    s2.metric(
        "Final Defender Strength",
        round(final_defense_strength, 2)
    )

    s3.metric(
        "Winner",
        "ATTACKERS" if attacker_wins else "DEFENDERS"
    )

    # ========================================================
    # FINAL TABLES
    # ========================================================

    st.subheader("Final Nation Strengths")

    fc1, fc2 = st.columns(2)

    with fc1:

        st.write("### Attackers")

        st.dataframe(
            pd.DataFrame({
                "Nation": list(final_attackers.keys()),
                "Strength": list(final_attackers.values())
            }),
            use_container_width=True
        )

    with fc2:

        st.write("### Defenders")

        st.dataframe(
            pd.DataFrame({
                "Nation": list(final_defenders.keys()),
                "Strength": list(final_defenders.values())
            }),
            use_container_width=True
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    st.subheader("Simulation Summary")

    st.markdown(f"""
    - Initial Attacker Strength:
      **{initial_attack_strength:.2f}**

    - Initial Defender Strength:
      **{initial_defense_strength:.2f}**

    - Neutral Strength:
      **{neutral_strength:.2f}**

    - Final Attacker Strength:
      **{final_attack_strength:.2f}**

    - Final Defender Strength:
      **{final_defense_strength:.2f}**

    - Victory Threshold:
      **{victory_threshold:.2f}**

    - Combat Strength Conserved:
      **{combat_strength:.2f}**

    - Result:
      ## {"⚔️ ATTACKERS WIN" if attacker_wins else "🛡️ DEFENDERS WIN"}
    """)
