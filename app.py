import altair as alt
import pandas as pd
import streamlit as st
from PIL import Image

# Define the data
def load_data():
    try:
        data = pd.read_excel('store.xlsx', engine='openpyxl')
    except FileNotFoundError:
        data = pd.DataFrame(
            columns=['Sole', 'Start', 'Finish', 'Event', 'Key Point'])
        data.to_excel('store.xlsx', index=False, engine='openpyxl')
    return data

data = load_data()

im = Image.open("icon.ico")

st.set_page_config(
    page_title="Modern History",
    page_icon=im,
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown('''
    <style>
    footer {visibility : hidden;}
    header {visibility : hidden;}
    </style>
''', unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>Modern History Timeline</h1>", unsafe_allow_html=True)

# Sidebar for user input
st.sidebar.header("Add Event")
sole = st.sidebar.text_input("Sole", value="")
start_date = st.sidebar.text_input("Start Date", value="")
finish_date = st.sidebar.text_input("Finish Date", value="")
event = st.sidebar.text_input("Event", value="")
key_point = st.sidebar.text_input("Key Point", value="")

# Submit button to add data to Excel sheet
if st.sidebar.button("Submit"):
    new_data = pd.DataFrame({
        'Sole': [sole],
        'Start': [start_date],
        'Finish': [finish_date],
        'Event': [event],
        'Key Point': [key_point]
    })
    # Ensure data is a DataFrame before appending
    if isinstance(data, pd.DataFrame):
        data = pd.concat([data, new_data], ignore_index=True)
        data.to_excel('store.xlsx', index=False, engine='openpyxl')

# Filter data based on search query
search_query = st.text_input("Search by Identity (Sole):")

# Filtered and sorted data
filtered_data = data[data['Sole'].str.contains(search_query, case=False)].sort_values('Finish')

filtered_data['IsMilestone'] = filtered_data['Start'] == filtered_data['Finish']

max_end_years = filtered_data.groupby('Sole')['Finish'].max().reset_index()
filtered_data = filtered_data.merge(max_end_years, on='Sole', suffixes=('', '_max'))

# Create the Gantt chart with bars for events with day range and diamond symbols for milestones
bars = alt.Chart(filtered_data).mark_bar().transform_filter(
    alt.datum.IsMilestone == False
).encode(
    x=alt.X('Start:T', title='Time', axis=alt.Axis(format='%d-%B-%Y')),
    x2=alt.X2('Finish:T'),
    y=alt.Y('Sole:N', title='Identity',sort=alt.SortField(field='Finish_max', order='ascending')),
    color=alt.Color('Sole:N', legend=None),
    tooltip=[
        alt.Tooltip('Sole:N'),
        alt.Tooltip('Start:T', format='%d-%B-%Y'),
        alt.Tooltip('Finish:T', format='%d-%B-%Y'),
        alt.Tooltip('Event:N'),
        alt.Tooltip('Key Point:N')
    ]
).properties(
    width=900
).interactive()

diamonds = alt.Chart(filtered_data).mark_point(shape='diamond', filled=True, size=300).transform_filter(
    alt.datum.IsMilestone == True
).encode(
    x=alt.X('Start:T', axis=alt.Axis(format='%d-%B-%Y')),
    y=alt.Y('Sole:N',sort=alt.SortField(field='Finish_max', order='ascending')),
    color=alt.Color('Sole:N', legend=None),
    tooltip=[
        alt.Tooltip('Sole:N'),
        alt.Tooltip('Start:T', format='%d-%B-%Y', title='On'),
        alt.Tooltip('Event:N'),
        alt.Tooltip('Key Point:N')
    ]
)

combined_chart = (bars + diamonds)

# Sort the chart based on finish time
combined_chart = combined_chart.configure_axis(
    labelFontSize=12,
)



st.altair_chart(combined_chart, use_container_width=True)
