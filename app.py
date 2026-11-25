
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed" / "analytics"

st.set_page_config(
    page_title="SkyLens | Aviation Intelligence",
    page_icon="✈️",
    layout="wide",
)


# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0B1120;
    }

    [data-testid="stSidebar"] {
        background-color: #111827;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #D1D5DB;
    }

    h1, h2, h3 {
        color: #F8FAFC;
    }

    div[data-testid="stMetric"] {
        background: #111827;
        border: 1px solid #263449;
        padding: 18px 20px;
        border-radius: 12px;
    }

    div[data-testid="stMetricLabel"] {
        color: #94A3B8;
    }

    div[data-testid="stMetricValue"] {
        color: #F8FAFC;
    }

    div[data-testid="stMetricDelta"] {
        color: #14B8A6;
    }

    div[data-testid="stPlotlyChart"] {
        background-color: #111827;
        border-radius: 12px;
        padding: 8px;
        border: 1px solid #263449;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #263449;
        border-radius: 10px;
    }

    .skylens-subtitle {
        color: #94A3B8;
        font-size: 15px;
    }

    .skylens-banner {
        background-color: #111827;
        border: 1px solid #263449;
        border-left: 4px solid #14B8A6;
        padding: 16px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }

    .skylens-banner-title {
        color: #14B8A6;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 1px;
    }

    .skylens-banner-text {
        color: #E2E8F0;
        font-size: 15px;
        margin-top: 6px;
    }

    hr {
        border-color: #263449;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATA
# ============================================================

@st.cache_data
def load_data():

    filenames = {
        "overall": "overall_performance.csv",
        "carrier": "carrier_performance.csv",
        "airport": "airport_performance.csv",
        "route": "route_performance.csv",
        "causes": "delay_cause_contributions.csv",
        "daily": "daily_performance.csv",
    }

    data = {}

    for key, filename in filenames.items():

        path = DATA_DIR / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Missing data file: {filename}"
            )

        data[key] = pd.read_csv(path)

    data["daily"]["flight_date"] = pd.to_datetime(
        data["daily"]["flight_date"]
    )

    return data


try:
    data = load_data()

except Exception as exc:
    st.error(f"Data loading failed: {exc}")
    st.stop()


overall = data["overall"].iloc[0]
carriers = data["carrier"].copy()
airports = data["airport"].copy()
routes = data["route"].copy()
causes = data["causes"].copy()
daily = data["daily"].copy()

routes["route"] = (
    routes["origin"] + "-" + routes["destination"]
)


# ============================================================
# CHART THEME
# ============================================================

CHART_BG = "#111827"
TEXT_COLOR = "#E2E8F0"
MUTED_COLOR = "#94A3B8"
ACCENT = "#14B8A6"
GRID_COLOR = "#263449"


def style_chart(fig, height=450):

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(
            family="Arial",
            color=TEXT_COLOR,
            size=12,
        ),
        title=dict(
            font=dict(
                size=18,
                color=TEXT_COLOR,
            ),
        ),
        height=height,
        margin=dict(
            l=30,
            r=25,
            t=65,
            b=40,
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
        ),
    )

    fig.update_xaxes(
        gridcolor=GRID_COLOR,
        zerolinecolor=GRID_COLOR,
    )

    fig.update_yaxes(
        gridcolor=GRID_COLOR,
        zerolinecolor=GRID_COLOR,
    )

    return fig


def show_chart(fig):

    st.plotly_chart(
        fig,
        width="stretch",
        theme=None,
    )


def number(value):

    return f"{value:,.0f}"


def pct(value):

    return f"{value:.2f}%"


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    """
    <div style="padding:10px 0 15px 0;">
        <div style="font-size:28px;font-weight:800;color:#F8FAFC;">
            ✈ SkyLens
        </div>
        <div style="color:#14B8A6;font-size:12px;
        letter-spacing:2px;font-weight:700;">
            AVIATION INTELLIGENCE
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Overview",
        "Carrier Intelligence",
        "Airport Intelligence",
        "Route Intelligence",
        "Delay Analysis",
        "Daily Trends",
    ],
)

st.sidebar.divider()

st.sidebar.markdown("### DATASET")

st.sidebar.markdown(
    """
    **Source:** BTS TranStats

    **Geography:** U.S. domestic

    **Period:** January 2025

    **Records:** 539,747
    """
)

st.sidebar.divider()

st.sidebar.caption(
    "Historical aviation analytics. "
    "Not a live flight tracking platform."
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    # ✈ SkyLens Aviation Intelligence

    <div class="skylens-subtitle">
    Aviation performance analytics for carriers, airports,
    routes and operational delay patterns.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="skylens-banner">
        <div class="skylens-banner-title">
            DATA COVERAGE
        </div>
        <div class="skylens-banner-text">
            January 1–31, 2025 |
            U.S. domestic reporting-carrier flights |
            BTS TranStats
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()


# ============================================================
# OVERVIEW
# ============================================================

if page == "Overview":

    st.subheader("Operational Overview")

    delay_rate = (
        overall["delayed_arrivals"]
        / overall["evaluated_arrivals"]
        * 100
    )

    cancellation_rate = (
        overall["cancellations"]
        / overall["total_flights"]
        * 100
    )

    row1 = st.columns(4)

    row1[0].metric(
        "Total Flights",
        number(overall["total_flights"]),
    )

    row1[1].metric(
        "Evaluated Arrivals",
        number(overall["evaluated_arrivals"]),
    )

    row1[2].metric(
        "Delayed Arrivals",
        number(overall["delayed_arrivals"]),
    )

    row1[3].metric(
        "Arrival Delay Rate",
        pct(delay_rate),
    )

    row2 = st.columns(4)

    row2[0].metric(
        "Cancellations",
        number(overall["cancellations"]),
    )

    row2[1].metric(
        "Cancellation Rate",
        pct(cancellation_rate),
    )

    row2[2].metric(
        "Diversions",
        number(overall["diversions"]),
    )

    row2[3].metric(
        "Average Signed Delay",
        f"{overall['avg_signed_arrival_delay']:.2f} min",
    )

    # --------------------------------------------------------
    # ANALYTICAL HIGHLIGHTS
    # --------------------------------------------------------

    st.markdown("### Analytical Highlights")

    highest_carrier = carriers.loc[
        carriers["delay_rate_pct"].idxmax()
    ]

    lowest_carrier = carriers.loc[
        carriers["delay_rate_pct"].idxmin()
    ]

    peak_day = daily.loc[
        daily["delay_rate_pct"].idxmax()
    ]

    largest_cause = causes.loc[
        causes["total_delay_minutes"].idxmax()
    ]

    insight1, insight2 = st.columns(2)

    with insight1:

        st.info(
            f"**Highest carrier delay rate:** "
            f"{highest_carrier['carrier']} — "
            f"{highest_carrier['delay_rate_pct']:.2f}%"
        )

        st.info(
            f"**Lowest carrier delay rate:** "
            f"{lowest_carrier['carrier']} — "
            f"{lowest_carrier['delay_rate_pct']:.2f}%"
        )

    with insight2:

        st.info(
            f"**Highest daily delay rate:** "
            f"{peak_day['flight_date'].strftime('%d %b %Y')} — "
            f"{peak_day['delay_rate_pct']:.2f}%"
        )

        st.info(
            f"**Largest delay-cause contributor:** "
            f"{largest_cause['delay_cause']} — "
            f"{largest_cause['contribution_pct']:.2f}%"
        )

    st.divider()

    # --------------------------------------------------------
    # OVERVIEW CHARTS
    # --------------------------------------------------------

    left, right = st.columns(2)

    with left:

        st.markdown("### Carrier Reliability")

        carrier_chart = carriers.sort_values(
            "delay_rate_pct",
            ascending=True,
        )

        fig = px.bar(
            carrier_chart,
            x="delay_rate_pct",
            y="carrier",
            orientation="h",
            color="delay_rate_pct",
            color_continuous_scale=[
                "#164E63",
                "#14B8A6",
            ],
            labels={
                "carrier": "Carrier",
                "delay_rate_pct": "Arrival Delay Rate (%)",
            },
        )

        fig.update_layout(
            coloraxis_showscale=False,
        )

        show_chart(style_chart(fig, 480))

    with right:

        st.markdown("### Daily Delay Trend")

        fig = px.line(
            daily,
            x="flight_date",
            y="delay_rate_pct",
            markers=True,
            labels={
                "flight_date": "Date",
                "delay_rate_pct": "Delay Rate (%)",
            },
        )

        fig.update_traces(
            line=dict(
                color=ACCENT,
                width=3,
            ),
            marker=dict(
                size=7,
            ),
        )

        show_chart(style_chart(fig, 480))

    st.divider()

    st.markdown("### Delay Cause Contribution")

    cause_chart = causes.sort_values(
        "total_delay_minutes",
        ascending=False,
    )

    fig = px.bar(
        cause_chart,
        x="delay_cause",
        y="total_delay_minutes",
        color="delay_cause",
        labels={
            "delay_cause": "Delay Cause",
            "total_delay_minutes": "Recorded Delay Minutes",
        },
    )

    show_chart(style_chart(fig, 420))

    st.caption(
        "Delay-cause contribution reflects recorded delay minutes, "
        "not the percentage of all flights affected."
    )


# ============================================================
# CARRIER INTELLIGENCE
# ============================================================

elif page == "Carrier Intelligence":

    st.subheader("Carrier Intelligence")

    st.caption(
        "Explore airline performance using carrier selection "
        "and arrival delay rate filters."
    )

    # --------------------------------------------------------
    # CARRIER SELECTION
    # --------------------------------------------------------

    options = sorted(carriers["carrier"].unique())

    selected = st.multiselect(
        "Select carriers",
        options,
        default=options,
    )

    if selected:

        selected_carriers = carriers[
            carriers["carrier"].isin(selected)
        ].copy()

        min_delay = float(
            selected_carriers["delay_rate_pct"].min()
        )

        max_delay = float(
            selected_carriers["delay_rate_pct"].max()
        )

        if min_delay < max_delay:

            delay_range = st.slider(
                "Filter by arrival delay rate (%)",
                min_value=min_delay,
                max_value=max_delay,
                value=(min_delay, max_delay),
            )

            filtered = selected_carriers[
                selected_carriers["delay_rate_pct"].between(
                    delay_range[0],
                    delay_range[1],
                )
            ].copy()

        else:

            filtered = selected_carriers.copy()

            st.caption(
                "Only one distinct delay rate is available "
                "for the selected carriers."
            )

    else:

        filtered = carriers.iloc[0:0].copy()

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    if filtered.empty:

        st.warning(
            "No carriers match the selected filters."
        )

    else:

        a, b, c = st.columns(3)

        a.metric(
            "Carriers Selected",
            len(filtered),
        )

        b.metric(
            "Total Flights",
            number(filtered["total_flights"].sum()),
        )

        c.metric(
            "Evaluated Arrivals",
            number(filtered["evaluated_arrivals"].sum()),
        )

        st.divider()

        # ----------------------------------------------------
        # DELAY RATE COMPARISON
        # ----------------------------------------------------

        st.markdown("### Carrier Delay Rate Comparison")

        fig = px.bar(
            filtered.sort_values(
                "delay_rate_pct",
                ascending=True,
            ),
            x="delay_rate_pct",
            y="carrier",
            orientation="h",
            color="delay_rate_pct",
            color_continuous_scale=[
                "#164E63",
                "#14B8A6",
            ],
            labels={
                "carrier": "Carrier",
                "delay_rate_pct": "Arrival Delay Rate (%)",
            },
        )

        fig.update_layout(
            coloraxis_showscale=False,
        )

        show_chart(style_chart(fig))

        # ----------------------------------------------------
        # FLIGHT VOLUME VS DELAY RATE
        # ----------------------------------------------------

        st.markdown(
            "### Carrier Volume vs Delay Rate"
        )

        fig = px.scatter(
            filtered,
            x="total_flights",
            y="delay_rate_pct",
            size="delayed_arrivals",
            color="carrier",
            hover_name="carrier",
            labels={
                "total_flights": "Total Flights",
                "delay_rate_pct": "Arrival Delay Rate (%)",
            },
        )

        show_chart(style_chart(fig))

        # ----------------------------------------------------
        # PERFORMANCE TABLE
        # ----------------------------------------------------

        st.markdown(
            "### Carrier Performance Table"
        )

        st.dataframe(
            filtered.sort_values(
                "delay_rate_pct",
                ascending=False,
            ),
            width="stretch",
            hide_index=True,
        )


# ============================================================
# AIRPORT INTELLIGENCE
# ============================================================

elif page == "Airport Intelligence":

    st.subheader("Airport Intelligence")

    options = sorted(airports["airport"].unique())

    selected = st.multiselect(
        "Filter destination airports",
        options,
        default=options,
    )

    filtered = airports[
        airports["airport"].isin(selected)
    ].copy()

    if filtered.empty:

        st.warning("Select at least one airport.")

    else:

        a, b, c = st.columns(3)

        a.metric(
            "Airports Selected",
            len(filtered),
        )

        b.metric(
            "Evaluated Arrivals",
            number(filtered["evaluated_arrivals"].sum()),
        )

        c.metric(
            "Delayed Arrivals",
            number(filtered["delayed_arrivals"].sum()),
        )

        st.divider()

        st.markdown("### Arrival Delay Rate by Airport")

        fig = px.bar(
            filtered.sort_values("delay_rate_pct"),
            x="delay_rate_pct",
            y="airport",
            orientation="h",
            color="delay_rate_pct",
            color_continuous_scale=[
                "#164E63",
                "#14B8A6",
            ],
            labels={
                "airport": "Airport",
                "delay_rate_pct": "Arrival Delay Rate (%)",
            },
        )

        fig.update_layout(
            coloraxis_showscale=False,
            height=650,
        )

        show_chart(style_chart(fig, 650))

        st.markdown("### Airport Volume vs Delay Rate")

        fig = px.scatter(
            filtered,
            x="evaluated_arrivals",
            y="delay_rate_pct",
            size="delayed_arrivals",
            color="airport",
            hover_name="airport",
            labels={
                "evaluated_arrivals": "Evaluated Arrivals",
                "delay_rate_pct": "Arrival Delay Rate (%)",
            },
        )

        show_chart(style_chart(fig))

        st.markdown("### Airport Performance Table")

        st.dataframe(
            filtered.sort_values(
                "delay_rate_pct",
                ascending=False,
            ),
            width="stretch",
            hide_index=True,
        )


# ============================================================
# ROUTE INTELLIGENCE
# ============================================================

elif page == "Route Intelligence":

    st.subheader("Route Intelligence")

    options = sorted(routes["route"].unique())

    selected = st.multiselect(
        "Filter directional routes",
        options,
        default=options,
    )

    filtered = routes[
        routes["route"].isin(selected)
    ].copy()

    if filtered.empty:

        st.warning("Select at least one route.")

    else:

        a, b, c = st.columns(3)

        a.metric(
            "Routes Selected",
            len(filtered),
        )

        b.metric(
            "Evaluated Arrivals",
            number(filtered["evaluated_arrivals"].sum()),
        )

        c.metric(
            "Delayed Arrivals",
            number(filtered["delayed_arrivals"].sum()),
        )

        st.divider()

        st.markdown("### Arrival Delay Rate by Directional Route")

        fig = px.bar(
            filtered.sort_values("delay_rate_pct"),
            x="delay_rate_pct",
            y="route",
            orientation="h",
            color="delay_rate_pct",
            color_continuous_scale=[
                "#164E63",
                "#14B8A6",
            ],
            labels={
                "route": "Directional Route",
                "delay_rate_pct": "Arrival Delay Rate (%)",
            },
        )

        fig.update_layout(
            coloraxis_showscale=False,
            height=650,
        )

        show_chart(style_chart(fig, 650))

        st.markdown("### Route Volume vs Delay Rate")

        fig = px.scatter(
            filtered,
            x="evaluated_arrivals",
            y="delay_rate_pct",
            size="delayed_arrivals",
            color="classification",
            hover_name="route",
            labels={
                "evaluated_arrivals": "Evaluated Arrivals",
                "delay_rate_pct": "Arrival Delay Rate (%)",
                "classification": "Classification",
            },
        )

        show_chart(style_chart(fig))

        st.markdown("### Route Performance Table")

        st.dataframe(
            filtered.sort_values(
                "delay_rate_pct",
                ascending=False,
            ),
            width="stretch",
            hide_index=True,
        )


# ============================================================
# DELAY ANALYSIS
# ============================================================

elif page == "Delay Analysis":

    st.subheader("Delay Analysis")

    a, b = st.columns(2)

    a.metric(
        "Recorded Delay Minutes",
        number(causes["total_delay_minutes"].sum()),
    )

    b.metric(
        "Delay Categories",
        len(causes),
    )

    st.divider()

    st.markdown("### Share of Recorded Delay Minutes by Cause")

    fig = px.pie(
        causes,
        names="delay_cause",
        values="total_delay_minutes",
        hole=0.5,
    )

    show_chart(style_chart(fig))

    st.markdown("### Delay Minutes by Cause")

    fig = px.bar(
        causes.sort_values(
            "total_delay_minutes",
            ascending=False,
        ),
        x="delay_cause",
        y="total_delay_minutes",
        color="delay_cause",
        labels={
            "delay_cause": "Delay Cause",
            "total_delay_minutes": "Delay Minutes",
        },
    )

    show_chart(style_chart(fig))

    st.markdown("### Delay Cause Metrics")

    st.dataframe(
        causes.sort_values(
            "total_delay_minutes",
            ascending=False,
        ),
        width="stretch",
        hide_index=True,
    )

    st.caption(
        "Delay-cause totals represent recorded delay minutes "
        "for flights with populated cause records."
    )


# ============================================================
# DAILY TRENDS
# ============================================================

elif page == "Daily Trends":

    st.subheader("Daily Operational Trends")

    start = daily["flight_date"].min().date()
    end = daily["flight_date"].max().date()

    date_range = st.date_input(
        "Reporting period",
        value=(start, end),
        min_value=start,
        max_value=end,
    )

    if len(date_range) == 2:

        start_date, end_date = date_range

        filtered = daily[
            (daily["flight_date"].dt.date >= start_date)
            & (daily["flight_date"].dt.date <= end_date)
        ].copy()

    else:

        filtered = daily.copy()

    if filtered.empty:

        st.warning("No data available for this date range.")

    else:

        a, b, c = st.columns(3)

        a.metric(
            "Days",
            len(filtered),
        )

        b.metric(
            "Evaluated Arrivals",
            number(filtered["evaluated_arrivals"].sum()),
        )

        c.metric(
            "Delayed Arrivals",
            number(filtered["delayed_arrivals"].sum()),
        )

        st.divider()

        # ----------------------------------------------------
        # DAILY DELAY RATE
        # ----------------------------------------------------

        st.markdown("### Daily Arrival Delay Rate")

        fig = px.line(
            filtered,
            x="flight_date",
            y="delay_rate_pct",
            markers=True,
            labels={
                "flight_date": "Date",
                "delay_rate_pct": "Arrival Delay Rate (%)",
            },
        )

        fig.update_traces(
            line=dict(
                color=ACCENT,
                width=3,
            ),
            marker=dict(
                size=7,
            ),
        )

        show_chart(style_chart(fig))

        # ----------------------------------------------------
        # DAILY DELAYED ARRIVALS
        # ----------------------------------------------------

        st.markdown("### Daily Delayed Arrivals")

        fig = px.bar(
            filtered,
            x="flight_date",
            y="delayed_arrivals",
            labels={
                "flight_date": "Date",
                "delayed_arrivals": "Delayed Arrivals",
            },
        )

        fig.update_traces(
            marker_color=ACCENT,
        )

        show_chart(style_chart(fig))

        # ----------------------------------------------------
        # DAILY METRICS TABLE
        # ----------------------------------------------------

        st.markdown("### Daily Metrics Table")

        st.dataframe(
            filtered,
            width="stretch",
            hide_index=True,
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center;color:#64748B;padding:10px;">
        <strong>SKYLENS AVIATION INTELLIGENCE</strong><br>
        Historical U.S. aviation analytics |
        BTS TranStats | January 2025
    </div>
    """,
    unsafe_allow_html=True,
)
