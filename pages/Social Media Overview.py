import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Load the CSV file
file_path = r"data\all_content.csv"
data = pd.read_csv(file_path)

# Ensure column names are consistent
data.columns = data.columns.str.strip()

# Preprocess data: convert strings with commas to numeric
data['Anzahl Likes'] = data['Anzahl Likes'].str.replace(',', '').astype(float)
data['Anzahl Kommentare'] = data['Anzahl Kommentare'].str.replace(',', '').astype(float)
data['Gesamtanzahl Reaktionen, Kommentare & Shares'] = data['Gesamtanzahl Reaktionen, Kommentare & Shares'].str.replace(',', '').astype(float)

# Convert 'Datum' to datetime
data['Datum'] = pd.to_datetime(data['Datum'], format='%d.%m.%y, %H:%M', errors='coerce')

# Streamlit app title
st.title('Social Media Overview')

# Sidebar for filtering options
st.sidebar.title("Filter Options")

# Multiselect for profiles with an 'All' option
profiles = data['Profil'].unique()
profiles_list = st.sidebar.multiselect("Select Profiles", options=['All'] + list(profiles), default=['All'])

# Determine the selected profiles
if 'All' in profiles_list:
    selected_profiles = profiles
else:
    selected_profiles = profiles_list

# Multiselect for platforms with an 'All' option
platforms = data['Platform'].unique()
platforms_list = st.sidebar.multiselect("Select Platforms", options=['All'] + list(platforms), default=['All'])

# Determine the selected profiles
if 'All' in platforms_list:
    selected_platforms = platforms
else:
    selected_platforms = platforms_list

# Text input for filtering by phrase in 'Text' column
phrase = st.sidebar.text_input("Enter a phrase to search in Text", value="")

# Filter data based on sidebar selections
filtered_data = data[
    (data['Profil'].isin(selected_profiles)) & 
    (data['Platform'].isin(selected_platforms))
]

# Apply text filter if a phrase is entered
if phrase:
    filtered_data = filtered_data[filtered_data['Nachricht'].str.contains(phrase, case=False, na=False)]

# Debugging: Show the count of filtered rows
st.write("Number of rows after filtering:", len(filtered_data))

# Ensure Datum is correctly parsed and contains no NaT values
if filtered_data['Datum'].isna().sum() > 0:
    st.write("Warning: Some 'Datum' values could not be parsed. They are excluded from plots.")
    filtered_data = filtered_data.dropna(subset=['Datum'])

# Sort data by 'Datum'
filtered_data = filtered_data.sort_values(by='Datum')

# Visualizations
st.write("## Visualizations")

# Using columns to display plots side-by-side
col1, col2 = st.columns(2)

# Show total likes over time in the first column
with col1:
    st.write("### Likes Over Time")
    if not filtered_data.empty and 'Datum' in filtered_data.columns:
        # Make a copy to avoid modifying the original DataFrame
        temp_data = filtered_data.copy()
        temp_data.set_index('Datum', inplace=True)
        st.line_chart(temp_data['Anzahl Likes'])

# Show comments over time in the second column
with col2:
    st.write("### Comments Over Time")
    if not filtered_data.empty and 'Datum' in filtered_data.columns:
        # Make a copy to avoid modifying the original DataFrame
        temp_data = filtered_data.copy()
        temp_data.set_index('Datum', inplace=True)
        st.line_chart(temp_data['Anzahl Kommentare'])

# Another row of side-by-side plots
col3, col4 = st.columns(2)

# Show total interactions over time in the first column
with col3:
    st.write("### Interactions Over Time")
    if not filtered_data.empty and 'Datum' in filtered_data.columns:
        # Make a copy to avoid modifying the original DataFrame
        temp_data = filtered_data.copy()
        temp_data.set_index('Datum', inplace=True)
        st.line_chart(temp_data['Gesamtanzahl Reaktionen, Kommentare & Shares'])

# Show interaction rate over time in the second column
with col4:
    st.write("### Interaction Rate Over Time")
    if not filtered_data.empty and 'Datum' in filtered_data.columns and 'Post-Interaktionsrate' in filtered_data.columns:
        # Make a copy to avoid modifying the original DataFrame
        temp_data = filtered_data.copy()
        temp_data.set_index('Datum', inplace=True)
        st.line_chart(temp_data['Post-Interaktionsrate'])