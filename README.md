Global CO2 Emission Dashboard

An interactive Dashboard built with Streamlit to analyse global CO2 and Greenhouse Gas Emission.Developed as part of the Data Science Lifecycle Module.

CO2 and Greenhouse Gas Emissions dataset from Our World In Data / World Bank.
Covers 217 countries across 76 indicators from 1750 to 2023.

Features used:
- Filter by country and year range using sidebar controls.
- Trend Tab: CO2 emissions over time with line and stacked area charts
- World Map Tab: choropleth map of emissions by country
- Rankings Tab: Top 15 countries by emissions with summary table.
- Deep Dive: all indicators for a single country with scatter plot

How to run locally
- Clone the repository
- install dependancies: pip install -r requirements.txt
- run the app: streamlit run app101.py

  Live app
  https://c02dashboard-dnztgasykffdqcvsp87k7n.streamlit.app/

  Technology used
  - Python
  - Streamlit
  - Plotly
  - Pandas
  - NumPy
