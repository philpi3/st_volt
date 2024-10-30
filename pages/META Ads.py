import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the new CSV file
new_data = pd.read_csv("pages/data/all_meta_ads.csv")

# Preprocess the new data
new_data.columns = new_data.columns.str.strip()

# Convert reporting dates to datetime
new_data['Reporting starts'] = pd.to_datetime(new_data['Reporting starts'])
new_data['Reporting ends'] = pd.to_datetime(new_data['Reporting ends'])

# Streamlit app title for the new page
st.title('Ad Campaign Analysis')

# Sidebar filters for campaign, ad set, and ad creative
campaign_names = new_data['Campaign name'].unique()
selected_campaigns = st.sidebar.multiselect("Select Campaigns", options=['All'] + list(campaign_names), default=['All'], key='campaigns')

ad_set_names = new_data['Ad Set Name'].unique()
selected_ad_sets = st.sidebar.multiselect("Select Ad Sets", options=['All'] + list(ad_set_names), default=['All'], key='ad_sets')

ad_names = new_data['Ad name'].unique()
selected_ads = st.sidebar.multiselect("Select Ads", options=['All'] + list(ad_names), default=['All'], key='ads')

# Date range selectors for comparison
date1_start = st.sidebar.date_input("Select Start Date 1", value=new_data['Reporting starts'].min(), key='date1_start')
date1_end = st.sidebar.date_input("Select End Date 1", value=new_data['Reporting ends'].max(), key='date1_end')
date2_start = st.sidebar.date_input("Select Start Date 2", value=new_data['Reporting starts'].min(), key='date2_start')
date2_end = st.sidebar.date_input("Select End Date 2", value=new_data['Reporting ends'].max(), key='date2_end')

# Apply filters
if 'All' in selected_campaigns:
    selected_campaigns = campaign_names
if 'All' in selected_ad_sets:
    selected_ad_sets = ad_set_names
if 'All' in selected_ads:
    selected_ads = ad_names

filtered_new_data = new_data[
    new_data['Campaign name'].isin(selected_campaigns) & 
    new_data['Ad Set Name'].isin(selected_ad_sets) & 
    new_data['Ad name'].isin(selected_ads)
]

# Filter data by selected date ranges
data_date1 = filtered_new_data[(filtered_new_data['Reporting starts'] >= pd.to_datetime(date1_start)) & 
                               (filtered_new_data['Reporting ends'] <= pd.to_datetime(date1_end))]

data_date2 = filtered_new_data[(filtered_new_data['Reporting starts'] >= pd.to_datetime(date2_start)) & 
                               (filtered_new_data['Reporting ends'] <= pd.to_datetime(date2_end))]






# Display data for date range 1
st.write(f"### Performance from {date1_start} to {date1_end}")
if not data_date1.empty:
    st.write("#### Amount Spent Over Time")
    st.line_chart(data_date1.set_index('Reporting starts')['Amount spent (EUR)'])
    
    st.write("#### Results Over Time")
    st.line_chart(data_date1.set_index('Reporting starts')['Results'])

    st.write("### Ad Performance Comparison")
    st.bar_chart(data_date1.set_index('Ad name')[['Impressions', 'Reach', 'Results']])

    st.write("### Cost Efficiency Analysis")
    st.scatter_chart(data_date1[['Cost per result', 'CPM (cost per 1,000 impressions)']])

    st.write("### Engagement Analysis")
    st.bar_chart(data_date1.set_index('Ad name')[['CTR (all)', 'ThruPlays']])

    # Conversion Rate Over Time
    st.write("### Conversion Rate Over Time")
    data_date1['Conversion Rate'] = data_date1['Results'] / data_date1['Impressions']
    st.line_chart(data_date1.set_index('Reporting starts')['Conversion Rate'])

    # Top Performing Ads
    st.write("### Top Performing Ads (Results)")
    top_ads_date1 = data_date1.nlargest(10, 'Results')
    st.bar_chart(top_ads_date1.set_index('Ad name')['Results'])

# Display data for date range 2
st.write(f"### Performance from {date2_start} to {date2_end}")
if not data_date2.empty:
    st.write("#### Amount Spent Over Time")
    st.line_chart(data_date2.set_index('Reporting starts')['Amount spent (EUR)'])
    
    st.write("#### Results Over Time")
    st.line_chart(data_date2.set_index('Reporting starts')['Results'])

    st.write("### Ad Performance Comparison")
    st.bar_chart(data_date2.set_index('Ad name')[['Impressions', 'Reach', 'Results']])

    st.write("### Cost Efficiency Analysis")
    st.scatter_chart(data_date2[['Cost per result', 'CPM (cost per 1,000 impressions)']])

    st.write("### Engagement Analysis")
    st.bar_chart(data_date2.set_index('Ad name')[['CTR (all)', 'ThruPlays']])

    # Conversion Rate Over Time
    st.write("### Conversion Rate Over Time")
    data_date2['Conversion Rate'] = data_date2['Results'] / data_date2['Impressions']
    st.line_chart(data_date2.set_index('Reporting starts')['Conversion Rate'])

    # Top Performing Ads
    st.write("### Top Performing Ads (Results)")
    top_ads_date2 = data_date2.nlargest(10, 'Results')
    st.bar_chart(top_ads_date2.set_index('Ad name')['Results'])
