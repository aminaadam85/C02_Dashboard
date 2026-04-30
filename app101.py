#  C02 Greenhouse Gas Emission 
# 5DATA004W - Data Science Project Lifecycle 
# Individual Coursework 
# Dataset: CO2 and Greenhouse Gas Emissions

# Import the libraries I need
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


# Set up the basic page settings
# This controls what shows in the browser tab and how the page is laid out
st.set_page_config(
    page_title="Global CO2 Emissions Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Custom styling for the dashboard
# I am using CSS to change the colours and fonts to make it look nicer
st.markdown("""
<style>

/* Import two fonts from Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

/* Set the default font for the whole app */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Clean white main background */
.stApp {
    background-color: white !important;
    color: #1a1a2e;
}

/* Steelblue sidebar */
[data-testid="stSidebar"] {
    background-color: steelblue !important;
    border-right: 2px solid dodgerblue;
}

/* White sidebar text */
[data-testid="stSidebar"] * {
    color: white !important;
}

/* Metric cards in dodgerblue with red left border for importance */
div[data-testid="metric-container"] {
    background-color: dodgerblue;
    border: 1px solid steelblue;
    border-left: 4px solid firebrick;
    border-radius: 12px;
    padding: 16px 20px;
}

/* Metric label text */
div[data-testid="metric-container"] label {
    color: aliceblue !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* Metric value in white so it pops */
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: white !important;
    font-family: 'Space Mono', monospace;
    font-size: 1.6rem !important;
}

/* H1 heading with red underline to make it stand out */
h1 {
    font-family: 'Space Mono', monospace !important;
    color: steelblue !important;
    font-size: 1.8rem !important;
    border-bottom: 3px solid firebrick;
    padding-bottom: 0.4rem;
}

/* H2 and H3 in steelblue */
h2, h3 {
    font-family: 'Space Mono', monospace !important;
    color: steelblue !important;
}

/* Tab bar in lightblue */
.stTabs [data-baseweb="tab-list"] {
    background-color: lightblue;
    border-radius: 8px;
    gap: 4px;
}

/* Inactive tabs in steelblue */
.stTabs [data-baseweb="tab"] {
    color: steelblue;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
}

/* Active tab in dodgerblue with white text */
.stTabs [aria-selected="true"] {
    background-color: dodgerblue !important;
    color: white !important;
    border-radius: 6px;
}

/* Widget labels */
.stSelectbox label, .stMultiSelect label, .stSlider label {
    color: white !important;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* Divider lines in lightblue */
hr {
    border-color: lightblue;
}

/* Alert boxes */
.stAlert {
    border-radius: 8px;
}

</style>
""", unsafe_allow_html=True)


# This function loads and cleans the dataset
# I am using st.cache_data so the data only loads once
# Without this it would reload every time the user changes a filter which would be slow
@st.cache_data
def load_data():

    # Read the CSV file from the same folder as this script
    df = pd.read_csv("OWID_CB_WIDEF_FINALDATA.csv")

    # I only want to keep 4 indicators that are most relevant to my analysis
    # These are the exact label strings used in the INDICATOR_LABEL column
    indicators = [
        "Annual CO2 emissions - Annual total emissions of carbon dioxide (CO2), excluding land-use change, measured in million tonnes.",
        "Annual CO2 emissions (per capita) - Annual total emissions of carbon dioxide (CO2), excluding land-use change, measured in tonnes per person.",
        "Share of contribution to global warming - Measured as a percentage of the world\u2019s temperature change.",
        "Change in global mean surface temperature caused by CO2 emissions - Measured in \u00b0C.",
    ]

    # Filter the dataframe to only keep rows that match those 4 indicators
    df_filtered = df[df["INDICATOR_LABEL"].isin(indicators)].copy()

    # Find the year columns by checking if the column name is a number
    # The dataset has one column per year like 1990, 1991, 1992 etc
    year_cols = [c for c in df_filtered.columns if str(c).isdigit()]

    # The data is currently in wide format with one column per year
    # I need to convert it to long format so each row has one year and one value
    # This makes it much easier to create charts with plotly
    df_long = df_filtered.melt(
        id_vars=["REF_AREA_LABEL", "INDICATOR_LABEL"],
        value_vars=year_cols,
        var_name="Year",
        value_name="Value",
    )

    # Convert the Year column from text to a number
    df_long["Year"] = df_long["Year"].astype(int)

    # Remove any rows where there is no value
    df_long = df_long.dropna(subset=["Value"])

    # Remove rows where the value is zero as these usually mean no data was recorded
    df_long = df_long[df_long["Value"] != 0]

    # Create shorter names for each indicator to use in chart labels
    label_map = {
        indicators[0]: "CO2 Emissions (Mt)",
        indicators[1]: "CO2 per Capita (t)",
        indicators[2]: "Share of Global Warming (%)",
        indicators[3]: "Temp Change from CO2 (degC)",
    }

    # Add a new column with the short indicator name
    df_long["Indicator"] = df_long["INDICATOR_LABEL"].map(label_map)

    # Remove regional groupings and keep only individual countries
    # These regional rows would distort the charts if left in
    regions_to_remove = [
        "World", "Asia", "Europe", "Africa", "Americas", "Oceania",
        "European Union", "G20", "G7", "OECD",
        "High-income countries", "Low-income countries",
        "Upper-middle-income countries", "Lower-middle-income countries",
    ]

    df_countries = df_long[~df_long["REF_AREA_LABEL"].isin(regions_to_remove)].copy()
    df_all = df_long.copy()

    return df_countries, df_all, label_map


# Try to load the data and catch any errors if the file is missing
try:
    df_countries, df_all, label_map = load_data()
    data_loaded = True
except FileNotFoundError:
    data_loaded = False


# Build the sidebar with the filter controls
with st.sidebar:
    st.markdown("## CO2 Dashboard")
    st.markdown("Global Emissions Analysis")
    st.divider()

    if data_loaded:
        # Get a sorted list of all country names in the dataset
        all_countries = sorted(df_countries["REF_AREA_LABEL"].unique().tolist())

        # Set some default countries to show when the app first loads
        default_countries = ["United States", "China", "India", "United Kingdom", "Germany", "Brazil"]
        default_countries = [c for c in default_countries if c in all_countries]

        # Country selection widget - user can pick one or more countries
        selected_countries = st.multiselect(
            "Select Countries",
            options=all_countries,
            default=default_countries,
        )

        # Get the min and max years from the dataset for the slider
        year_min = int(df_countries["Year"].min())
        year_max = int(df_countries["Year"].max())

        # Year range slider - user picks a start and end year
        year_range = st.slider(
            "Select Year Range",
            min_value=year_min,
            max_value=year_max,
            value=(1990, year_max),
        )

        # Dropdown to choose which indicator to show in the main charts
        indicator_options = list(label_map.values())
        selected_indicator = st.selectbox(
            "Select Indicator",
            options=indicator_options,
            index=0,
        )

        st.divider()
        st.markdown("Data source: Our World in Data / World Bank")


# If the CSV file was not found then show an error and stop the app
if not data_loaded:
    st.error("Could not find the data file. Please make sure OWID_CB_WIDEF_FINALDATA.csv is in the same folder as this script.")
    st.stop()

# If the user has removed all countries then show a warning and stop
# This prevents errors from trying to draw charts with no data
if not selected_countries:
    st.warning("Please select at least one country from the sidebar.")
    st.stop()


# Filter the data based on what the user has selected in the sidebar
country_and_year_filter = (
    df_countries["REF_AREA_LABEL"].isin(selected_countries)
    & df_countries["Year"].between(year_range[0], year_range[1])
)

df_selected = df_countries[country_and_year_filter]

# Further filter to only the chosen indicator for the indicator specific charts
df_indicator = df_selected[df_selected["Indicator"] == selected_indicator]


# Main dashboard title and subtitle
st.markdown("# Global CO2 Emissions Dashboard")
st.markdown(
    f"<p style='color:steelblue;margin-top:-10px'>Showing {len(selected_countries)} countries from {year_range[0]} to {year_range[1]}</p>",
    unsafe_allow_html=True,
)


# KPI summary cards shown at the top of the dashboard
# These give the user a quick overview of the current data selection

# Find the most recent year that has data
latest_year = df_indicator["Year"].max() if not df_indicator.empty else year_range[1]
df_latest_year = df_indicator[df_indicator["Year"] == latest_year]

# Create 4 columns for the 4 metric cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    # Show the total if looking at overall emissions or the average for other indicators
    if selected_indicator == "CO2 Emissions (Mt)":
        summary_value = df_latest_year["Value"].sum()
        card_label = f"Total in {latest_year}"
    else:
        summary_value = df_latest_year["Value"].mean()
        card_label = f"Average in {latest_year}"
    st.metric(card_label, f"{summary_value:,.1f}")

with col2:
    # Show the country with the highest value
    top_country = df_latest_year.nlargest(1, "Value")
    if not top_country.empty:
        st.metric("Top Emitter", top_country.iloc[0]["REF_AREA_LABEL"], f"{top_country.iloc[0]['Value']:,.1f}")

with col3:
    # Calculate the year on year percentage change
    two_years = df_indicator[df_indicator["Year"].isin([latest_year, latest_year - 1])]
    if len(two_years["Year"].unique()) == 2:
        value_now = two_years[two_years["Year"] == latest_year]["Value"].sum()
        value_before = two_years[two_years["Year"] == latest_year - 1]["Value"].sum()
        change = ((value_now - value_before) / value_before * 100) if value_before else 0
        st.metric("Year on Year Change", f"{change:+.1f}%", delta=f"{change:+.1f}%")
    else:
        st.metric("Countries Selected", len(selected_countries))

with col4:
    # Show how many years are covered by the slider selection
    st.metric("Years Covered", f"{year_range[1] - year_range[0]} years", f"{year_range[0]} to {year_range[1]}")

st.divider()


# Create the 4 tabs for different views of the data
tab1, tab2, tab3, tab4 = st.tabs([
    "Trends",
    "World Map",
    "Rankings",
    "Deep Dive",
])


# TAB 1 - TRENDS
# Shows the selected indicator over time as a line chart
# Also shows a stacked area chart of total CO2 emissions
with tab1:
    st.subheader(f"{selected_indicator} Over Time")

    if df_indicator.empty:
        st.info("No data available for the current selection.")
    else:
        # Line chart showing each country as a separate coloured line
        line_chart = px.line(
            df_indicator.sort_values("Year"),
            x="Year",
            y="Value",
            color="REF_AREA_LABEL",
            labels={"Value": selected_indicator, "REF_AREA_LABEL": "Country"},
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        line_chart.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="aliceblue",
            legend_title="Country",
            hovermode="x unified",
            font=dict(family="DM Sans", color="#1a1a2e"),
            xaxis=dict(gridcolor="lightblue"),
            yaxis=dict(gridcolor="lightblue"),
        )
        line_chart.update_traces(line_width=2.5)
        st.plotly_chart(line_chart, use_container_width=True)

    # Stacked area chart always shows CO2 total regardless of selected indicator
    st.subheader("Stacked CO2 Emissions (Mt)")
    df_co2_total = df_selected[df_selected["Indicator"] == "CO2 Emissions (Mt)"]

    if not df_co2_total.empty:
        area_chart = px.area(
            df_co2_total.sort_values("Year"),
            x="Year",
            y="Value",
            color="REF_AREA_LABEL",
            labels={"Value": "CO2 (Mt)", "REF_AREA_LABEL": "Country"},
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        area_chart.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="aliceblue",
            xaxis=dict(gridcolor="lightblue"),
            yaxis=dict(gridcolor="lightblue"),
            font=dict(family="DM Sans", color="#1a1a2e"),
        )
        st.plotly_chart(area_chart, use_container_width=True)


# TAB 2 - WORLD MAP
# Shows a colour coded world map for the selected indicator and year
with tab2:
    st.subheader(f"World Map - {selected_indicator}")

    # Slider to pick which year to show on the map
    map_year = st.slider(
        "Select year for map",
        min_value=year_range[0],
        max_value=year_range[1],
        value=year_range[1],
        key="map_year",
    )

    # Use all countries for the map not just the sidebar selection
    # This gives a full global picture
    df_map_data = df_countries[
        (df_countries["Indicator"] == selected_indicator)
        & (df_countries["Year"] == map_year)
    ]

    if df_map_data.empty:
        st.info("No data available for the selected year.")
    else:
        world_map = px.choropleth(
            df_map_data,
            locations="REF_AREA_LABEL",
            locationmode="country names",
            color="Value",
            hover_name="REF_AREA_LABEL",
            color_continuous_scale="Reds",
            labels={"Value": selected_indicator},
            template="plotly_white",
            title=f"{selected_indicator} in {map_year}",
        )
        world_map.update_layout(
            paper_bgcolor="white",
            geo=dict(bgcolor="aliceblue", showframe=False),
            coloraxis_colorbar=dict(title=selected_indicator, thickness=15),
            font=dict(family="DM Sans", color="#1a1a2e"),
            margin=dict(l=0, r=0, t=40, b=0),
        )
        st.plotly_chart(world_map, use_container_width=True)


# TAB 3 - RANKINGS
# Shows the top N countries as a horizontal bar chart for a chosen year
with tab3:
    st.subheader(f"Country Rankings - {selected_indicator}")

    # Slider to pick the year for rankings
    rank_year = st.slider(
        "Select year for rankings",
        min_value=year_range[0],
        max_value=year_range[1],
        value=year_range[1],
        key="rank_year",
    )

    # Slider to control how many countries appear in the chart
    number_of_countries = st.slider("How many countries to show", 5, 30, 15, key="top_n")

    # Get the top N countries by value for the chosen year
    df_rankings = df_countries[
        (df_countries["Indicator"] == selected_indicator)
        & (df_countries["Year"] == rank_year)
    ].nlargest(number_of_countries, "Value")

    if df_rankings.empty:
        st.info("No data available.")
    else:
        bar_chart = px.bar(
            df_rankings.sort_values("Value"),
            x="Value",
            y="REF_AREA_LABEL",
            orientation="h",
            color="Value",
            color_continuous_scale="Reds",
            labels={"Value": selected_indicator, "REF_AREA_LABEL": "Country"},
            template="plotly_white",
            title=f"Top {number_of_countries} Countries in {rank_year}",
        )
        bar_chart.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="aliceblue",
            yaxis=dict(categoryorder="total ascending"),
            coloraxis_showscale=False,
            font=dict(family="DM Sans", color="#1a1a2e"),
            xaxis=dict(gridcolor="lightblue"),
        )
        st.plotly_chart(bar_chart, use_container_width=True)

    # Show a simple data table for the sidebar selected countries
    st.subheader("Summary Table")
    df_table = df_countries[
        (df_countries["REF_AREA_LABEL"].isin(selected_countries))
        & (df_countries["Indicator"] == selected_indicator)
        & (df_countries["Year"] == rank_year)
    ][["REF_AREA_LABEL", "Value"]].rename(
        columns={"REF_AREA_LABEL": "Country", "Value": selected_indicator}
    ).sort_values(selected_indicator, ascending=False).reset_index(drop=True)

    st.dataframe(df_table, use_container_width=True)


# TAB 4 - DEEP DIVE
# Shows all 4 indicators for one country in stacked charts
# Also shows a scatter chart comparing total vs per capita emissions
with tab4:
    st.subheader("All Indicators for One Country")

    # Let the user pick a single country to focus on
    chosen_country = st.selectbox(
        "Select a country to explore",
        options=selected_countries if selected_countries else all_countries[:10],
        key="deep_country",
    )

    # Get all data for that country within the selected year range
    df_one_country = df_countries[
        (df_countries["REF_AREA_LABEL"] == chosen_country)
        & (df_countries["Year"].between(year_range[0], year_range[1]))
    ]

    if df_one_country.empty:
        st.info("No data available for this country.")
    else:
        # Get the list of indicators that have data for this country
        available_indicators = df_one_country["Indicator"].unique().tolist()

        # Create one subplot row per indicator all sharing the same x axis
        subplot_fig = make_subplots(
            rows=len(available_indicators),
            cols=1,
            shared_xaxes=True,
            subplot_titles=available_indicators,
            vertical_spacing=0.08,
        )

        # Colours for each indicator line using blues and reds
        line_colours = ["steelblue", "firebrick", "dodgerblue", "indianred"]

        # Add a line for each indicator to its own subplot row
        for i, indicator_name in enumerate(available_indicators):
            df_sub = df_one_country[df_one_country["Indicator"] == indicator_name].sort_values("Year")
            subplot_fig.add_trace(
                go.Scatter(
                    x=df_sub["Year"],
                    y=df_sub["Value"],
                    mode="lines+markers",
                    name=indicator_name,
                    line=dict(color=line_colours[i % len(line_colours)], width=2),
                    marker=dict(size=4),
                ),
                row=i + 1,
                col=1,
            )

        subplot_fig.update_layout(
            height=250 * len(available_indicators),
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="aliceblue",
            font=dict(family="DM Sans", color="#1a1a2e"),
            showlegend=False,
            title_text=f"All Indicators for {chosen_country}",
        )

        # Apply grid styling to each subplot
        for i in range(1, len(available_indicators) + 1):
            subplot_fig.update_xaxes(gridcolor="lightblue", row=i, col=1)
            subplot_fig.update_yaxes(gridcolor="lightblue", row=i, col=1)

        st.plotly_chart(subplot_fig, use_container_width=True)

    # Scatter chart comparing total CO2 vs per capita CO2 for all countries
    st.subheader("Total CO2 vs Per Capita CO2")

    scatter_year = st.slider(
        "Select year for scatter chart",
        min_value=year_range[0],
        max_value=year_range[1],
        value=year_range[1],
        key="scatter_year",
    )

    # Get total emissions data for all countries in the chosen year
    df_totals = df_countries[
        (df_countries["Indicator"] == "CO2 Emissions (Mt)")
        & (df_countries["Year"] == scatter_year)
    ].rename(columns={"Value": "CO2_Total"})

    # Get per capita data for all countries in the chosen year
    df_per_capita = df_countries[
        (df_countries["Indicator"] == "CO2 per Capita (t)")
        & (df_countries["Year"] == scatter_year)
    ].rename(columns={"Value": "CO2_PerCapita"})

    # Join both datasets on country name
    df_scatter_data = df_totals.merge(df_per_capita, on="REF_AREA_LABEL")

    if not df_scatter_data.empty:
        scatter_chart = px.scatter(
            df_scatter_data,
            x="CO2_Total",
            y="CO2_PerCapita",
            hover_name="REF_AREA_LABEL",
            size="CO2_Total",
            size_max=60,
            color="CO2_PerCapita",
            color_continuous_scale="Blues",
            labels={
                "CO2_Total": "Total CO2 (Mt)",
                "CO2_PerCapita": "CO2 per Capita (t)",
            },
            template="plotly_white",
            title=f"Total Emissions vs Per Capita in {scatter_year}",
        )
        scatter_chart.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="aliceblue",
            xaxis=dict(gridcolor="lightblue"),
            yaxis=dict(gridcolor="lightblue"),
            font=dict(family="DM Sans", color="#1a1a2e"),
        )

        # Highlight selected countries with a red star marker so they stand out
        df_highlighted = df_scatter_data[df_scatter_data["REF_AREA_LABEL"].isin(selected_countries)]
        scatter_chart.add_trace(go.Scatter(
            x=df_highlighted["CO2_Total"],
            y=df_highlighted["CO2_PerCapita"],
            mode="markers+text",
            text=df_highlighted["REF_AREA_LABEL"],
            textposition="top center",
            marker=dict(color="firebrick", size=10, symbol="star"),
            name="Selected Countries",
            showlegend=True,
        ))

        st.plotly_chart(scatter_chart, use_container_width=True)