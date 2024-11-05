import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')
import plotly.express as px

merged_data = pd.read_csv("data/cleaned_data.csv")

merged_data.head()

all_years =  sorted(merged_data['year'].unique())

def get_daily_quality_air(df :pd.DataFrame, station :str, columms :list) -> pd.DataFrame:
    station_data = df[df['station'] == station]
    daily_quality_df = station_data.groupby(['year', 'month', 'day'])[columms].mean().reset_index()
    return daily_quality_df

def get_quality_air_by_season(df :pd.DataFrame, station: str, columns: list, season: str) ->pd.DataFrame:
    station_data = df[df['station'] == station]
    if season == 'spring':
        station_data = station_data[station_data['month'].between(3, 5)]
    elif season == 'summer':
        station_data = station_data[station_data['month'].between(6, 8)]
    elif season == 'winter':
         station_data = station_data[((station_data['month'] == 12) & (station_data['year'] == station_data['year'].max() - 1)) | 
                                    ((station_data['month'].between(1, 2)) & (station_data['year'] == station_data['year'].max()))]
    elif season == 'fall':
        station_data = station_data[station_data['month'].between(9, 11)]

    air_quality_df = station_data.groupby(['year', 'month', 'day'])[columns].mean().reset_index()
    return air_quality_df

def get_hourly_change_air(df: pd.DataFrame, station: str, columns: list) -> pd.DataFrame:
    station_data = df[df['station'] == station]
    daily_quality_df = station_data.groupby('hour')[columns].mean().reset_index()
    return daily_quality_df
    

st.header('Air Quality Dashboard :sparkles:')

with st.sidebar:
    selected_station = st.selectbox('Pilih Stasiun', merged_data['station'].unique())

st.subheader('Daily Air Quality')

particle_daily_quality_df = get_daily_quality_air(merged_data, selected_station, ['PM10', 'PM2.5'])

gases_daily_quality_df = get_daily_quality_air(merged_data, selected_station, [ 'NO2', 'SO2','O3'])


particle_daily_quality_df['date'] = pd.to_datetime(particle_daily_quality_df[['year', 'month', 'day']])

gases_daily_quality_df['date'] = pd.to_datetime(gases_daily_quality_df[['year', 'month', 'day']])

co_daily_quality_df = get_daily_quality_air(merged_data, selected_station, ['CO'])
co_daily_quality_df['date'] = pd.to_datetime(co_daily_quality_df[['year', 'month', 'day']])


# Create the Plotly figure
fig = px.line(
    particle_daily_quality_df, 
    x='date', 
    y=['PM10', 'PM2.5'],
    title=f'Daily Air Quality in {selected_station} (Particles)',
    labels={'value': 'Concentration (µg/m³)', 'day': 'Day', 'variable': 'Pollutant'}
)

# Customize the layout for better readability
fig.update_layout(
    xaxis_title='Day of the Month',
    yaxis_title='Pollutant Concentration (µg/m³)',
    legend_title='Pollutant',
    hovermode="x unified"  # Show hover data for all lines on the same x-axis point
)

# create the plotly figure for gases
fig_gases = px.line(
    gases_daily_quality_df, 
    x='date', 
    y=['NO2', 'SO2','O3'],
    title=f'Daily Air Quality in {selected_station} (Gases)',
    labels={'value': 'Concentration (µg/m³)', 'day': 'Day',
            'variable': 'Pollutant'}
)

# Customize the layout for better readability
fig_gases.update_layout(
    xaxis_title='Day of the Month',
    yaxis_title='Pollutant Concentration (µg/m³)',
    legend_title='Pollutant',
    hovermode="x unified"  # Show hover data for all lines on the same x-axis point
)

# create the plotly figure for gases
fig_co = px.line(
    co_daily_quality_df, 
    x='date', 
    y=['CO'],
    title=f'Daily Air Quality in {selected_station} (CO)',
    labels={'value': 'Concentration (µg/m³)', 'day': 'Day',
            'variable': 'Pollutant'}
)

# Customize the layout for better readability
fig_co.update_layout(
    xaxis_title='Day of the Month',
    yaxis_title='Pollutant Concentration (µg/m³)',
    legend_title='Pollutant',
    hovermode="x unified"  # Show hover data for all lines on the same x-axis point
)

# Display the plot using Streamlit
st.plotly_chart(fig)
st.plotly_chart(fig_gases)  # Display the plot for gases
st.plotly_chart(fig_co)  # Display the plot for gases

st.subheader('Seasonal Air Quality')
# create the plotly figure for seasonal quality


winter_quality_df = get_quality_air_by_season(merged_data, selected_station, ['PM10', 'PM2.5','TEMP'], 'winter')

winter_quality_gases = get_quality_air_by_season(merged_data, selected_station, ['NO2', 'SO2','O3','TEMP'], 'winter')


fig_winter = px.scatter(
    winter_quality_df, 
    x='TEMP', 
    y=['PM10', 'PM2.5'],
    title=f'Seasonal Air Quality in {selected_station} (Winter)',
    labels={'value': 'Concentration (µg/m³)', 'day': 'Day',
            'variable': 'Pollutant'},
    trendline="ols",  # Add a linear regression trendline
    # color='month',
)

# Customize the layout for better readability
fig_winter.update_layout(
    xaxis_title='Temperature (°C)',
    yaxis_title='Pollutant Concentration (µg/m³)',
    legend_title='Pollutant',
    hovermode="x unified" 
)

fig_winter_gas = px.scatter(
    winter_quality_gases, 
    x='TEMP', 
    y=['NO2', 'SO2','O3'],
    title=f'Seasonal Air Quality in {selected_station} (Winter)',
    labels={'value': 'Concentration (µg/m³)', 'day': 'Day',
            'variable': 'Pollutant'},
    trendline="ols",  # Add a linear regression trendline
    # color='month',
)

# Customize the layout for better readability
fig_winter_gas.update_layout(
    xaxis_title='Temperature (°C)',
    yaxis_title='Pollutant Concentration (µg/m³)',
    legend_title='Pollutant',
    hovermode="x unified" 
)

st.plotly_chart(fig_winter)
st.plotly_chart(fig_winter_gas)


st.subheader('Hours of Worsening Air Quality')

particle_hourly_change_df = get_hourly_change_air(merged_data, selected_station, ['PM10', 'PM2.5'])
gases_hourly_change_df = get_hourly_change_air(merged_data, selected_station, ['NO2', 'SO2', 'O3',])

# Create the Plotly figure for particles
fig_hourly_change_particles = px.bar(
    particle_hourly_change_df,
    x='hour',
    y=['PM10', 'PM2.5'],
    title=f'Hourly Change in Air Quality in {selected_station} (Particles)',
    labels={'value': 'Change in Concentration (µg/m³)', 'hour': 'Hour', 'variable': 'Pollutant'}
)

# Customize the layout for better readability
fig_hourly_change_particles.update_layout(
    xaxis_title='Hour of the Day',
    yaxis_title='Change in Pollutant Concentration (µg/m³)',
    legend_title='Pollutant',
    hovermode="x unified"
)

# Create the Plotly figure for gases
fig_hourly_change_gases = px.bar(
    gases_hourly_change_df,
    x='hour',
    y=['NO2', 'SO2', 'O3'],
    title=f'Hourly Change in Air Quality in {selected_station} (Gases)',
    labels={'value': 'Change in Concentration (µg/m³)', 'hour': 'Hour', 'variable': 'Pollutant'}
)

# Customize the layout for better readability
fig_hourly_change_gases.update_layout(
    xaxis_title='Hour of the Day',
    yaxis_title='Change in Pollutant Concentration (µg/m³)',
    legend_title='Pollutant',
    hovermode="x unified"
)

# Display the plots using Streamlit
st.plotly_chart(fig_hourly_change_particles)
st.plotly_chart(fig_hourly_change_gases)