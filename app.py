import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = (
"/home/rhyme/Desktop/Project/Motor_Vehicle_Collisions_-_Crashes.csv"
)

# Title and subheading
st.title("Motor Vehicle Collisions in New York City")
st.markdown("## A streamlit dashboard to visualise and analyse vehicle collisions in NYC.")

# Decorator that ensures no waste of CPU
@st.cache(persist=True)
# Function to load DATA
def load_data(nrows):
    # Reads csv data
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
    # Drops invalid values for latitude and longitude
    data.dropna(subset = ['LATITUDE', 'LONGITUDE'], inplace= True)
    # Make each column lower case
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis = 'columns', inplace = True)
    data.rename(columns = {'crash_date_crash_time': 'date/time'}, inplace = True)
    return data

# Load first 100k data rows
data = load_data(100000)
original_data = data

st.header("Where are the most people injured in NYC?")
injured_people = st.slider("Number of people injured in vehicle collisions", 0, 19) # Max no. of injuries
# Maps the data query of injured people
st.map(data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how = "any")) # Drops the row includiong any invalid values

# Collisions by time
st.header("How many collisions occur during a given time of day?")
hour = st.slider("Hour to look at", 0, 23)
data = data[data['date/time'].dt.hour == hour] # Data at a certain CRASH_TIME

st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour + 1) % 24))

# Mid points of all data points
midpoint = (np.average(data['latitude']), np.average(data["longitude"]))

st.write(pdk.Deck(
    map_style = "mapbox://styles/mapbox/light-v9",
    # Initialise the map over NYC
    initial_view_state = {
    "latitude": midpoint[0],
    "longitude": midpoint[1],
    "zoom": 11,
    "pitch": 50,

    },

    layers = [
        pdk.Layer(
        "HexagonLayer",
        data = data[["date/time", "latitude", 'longitude']],
        get_position = ['longitude', 'latitude'],
        radius = 100,
        extruded = True,
        pickable = True,
        elevation_scale = 4,
        elevation_range = [0, 1000],

        ),
    ],

))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))

# Filter data to between specified hour
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))

]

# Histogram plot
hist = np.histogram(filtered['date/time'].dt.minute, bins = 60, range=(0, 60))[0]

# Data frame
chart_data = pd.DataFrame({'minute':range(60), 'crashes':hist})

# plot the figure
fig = px.bar(chart_data, x = 'minute', y = 'crashes', hover_data = ['minute', 'crashes'], height = 400)
st.write(fig)

st.header("Top 5 dangerous streets by affected type of people")
select = st.selectbox("Affected type of people", ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrians':
    # Query the data for injured pedestrians for the street name, sorted by descending order
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by = ['injured_pedestrians'], ascending = False).dropna(how = 'any')[:5])

elif select == 'Cyclists':
    # Query the data for injured cyclists for the street name, sorted by descending order
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by = ['injured_cyclists'], ascending = False).dropna(how = 'any')[:5])

else:
    # Query the data for injured motorists for the street name, sorted by descending order
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by = ['injured_motorists'], ascending = False).dropna(how = 'any')[:5])










# Checkbox for user to select
if st.checkbox("Show Raw Data", False):

    # Shows the raw data on the dashboard
    st.subheader('Raw Data')
    st.write(data)
