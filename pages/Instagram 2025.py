import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

st.set_page_config(layout="wide")

# Load the CSV file

data = pd.read_csv("pages/data/Jan25-04.02.csv")

# Normalize the sentiment and politikfeld columns by stripping extra quotes and whitespace
data['sentiment'] = data['sentiment'].str.strip(" '")
data['politikfeld'] = data['politikfeld'].str.strip(" '")
data['emotion'] = data['emotion'].str.strip(" '")


# Ensure column names are consistent
data.columns = data.columns.str.strip()

# Preprocess data: convert strings with commas to numeric
data['Anzahl Likes'] = data['Anzahl Likes'].str.replace(',', '').astype(float)
data['Anzahl Kommentare'] = data['Anzahl Kommentare'].str.replace(',', '').astype(float)
data['Reaktionen, Kommentare & Shares'] = data['Reaktionen, Kommentare & Shares'].str.replace(',', '').astype(float)
data['Post-Interaktionsrate'] = data['Post-Interaktionsrate'].str.replace(',', '.').astype(float)

# Convert 'Datum' to datetime
data['Datum'] = data['Datum'].str.replace(',', ' ')

data['Datum'] = pd.to_datetime(data['Datum'], format='%d.%m.%y %H:%M', errors='coerce')

# Streamlit app title
st.title('Social Media Post Analysis')

# Sidebar for filtering options
st.sidebar.title("Filter Options")

# Multiselect for groups with an 'All' option
groups = data['Gruppe'].unique()
groups_list = st.sidebar.multiselect("Select Group", options=['All'] + list(groups), default=['All'])

# Determine the selected groups
if 'All' in groups_list:
    selected_groups = groups
else:
    selected_groups = groups_list

# Multiselect for profiles with an 'All' option
profiles = data['Profil'].unique()
profiles_list = st.sidebar.multiselect("Select Profiles", options=['All'] + list(profiles), default=['All'])

# Determine the selected profiles
if 'All' in profiles_list:
    selected_profiles = profiles
else:
    selected_profiles = profiles_list

# Multiselect for sentiments with an 'All' option
sentiments = data['sentiment'].unique()
sentiments_list = st.sidebar.multiselect("Select Sentiments", options=['All'] + list(sentiments), default=['All'])

# Determine the selected sentiments
if 'All' in sentiments_list:
    selected_sentiments = sentiments
else:
    selected_sentiments = sentiments_list

# Multiselect for politikfeld with an 'All' option
politikfelds = data['politikfeld'].unique()
politikfeld_list = st.sidebar.multiselect("Select Politikfeld", options=['All'] + list(politikfelds), default=['All'])

# Determine the selected politikfelds
if 'All' in politikfeld_list:
    selected_politikfeld = politikfelds
else:
    selected_politikfeld = politikfeld_list

# Multiselect for emotion with an 'All' option
emotions = data['emotion'].unique()
emotions_list = st.sidebar.multiselect("Select Emotions", options=['All'] + list(emotions), default=['All'])

# Determine the selected emotions
if 'All' in emotions_list:
    selected_emotions = emotions
else:
    selected_emotions = emotions_list

# Text input for filtering by phrase in 'Text' column
phrase = st.sidebar.text_input("Enter a phrase to search in Text", value="")

# Filter data based on sidebar selections
filtered_data = data[
    (data['Profil'].isin(selected_profiles)) & 
    (data['sentiment'].isin(selected_sentiments)) &
    (data['politikfeld'].isin(selected_politikfeld)) &
    (data['emotion'].isin(selected_emotions)) &
    (data['Gruppe'].isin(selected_groups))
]

# Apply text filter if a phrase is entered
if phrase:
    filtered_data = filtered_data[filtered_data['Text'].str.contains(phrase, case=False, na=False)]

#TEST BELOW
# Ensure that 'Post-Interaktionsrate' is numeric
if 'Post-Interaktionsrate' in filtered_data.columns:
    
    filtered_data['Post-Interaktionsrate'] = pd.to_numeric(filtered_data['Post-Interaktionsrate'], errors='coerce')
    
    # Calculate the average interaction rate per category
    sentiment_perf = filtered_data.groupby('sentiment')['Post-Interaktionsrate'].mean()
    emotion_perf = filtered_data.groupby('emotion')['Post-Interaktionsrate'].mean()
    politikfeld_perf = filtered_data.groupby('politikfeld')['Post-Interaktionsrate'].mean()

    # Debug: print the indexes so we can see what keys are available
    #st.write("Sentiment groups:", sentiment_perf.index.tolist())
    #st.write("Emotion groups:", emotion_perf.index.tolist())
    #st.write("Politikfeld groups:", politikfeld_perf.index.tolist())

    # Check if the series are non-empty before proceeding
    if not sentiment_perf.empty and not emotion_perf.empty and not politikfeld_perf.empty:
        try:
            best_sentiment = sentiment_perf.idxmax()
            # Check that the key exists before indexing
            if best_sentiment in sentiment_perf.index:
                best_sentiment_rate = sentiment_perf.loc[best_sentiment]
            else:
                best_sentiment_rate = float('nan')
        except Exception as e:
            best_sentiment = "N/A"
            best_sentiment_rate = 0
            st.error(f"Error determining best sentiment: {e}")

        try:
            best_emotion = emotion_perf.idxmax()
            if best_emotion in emotion_perf.index:
                best_emotion_rate = emotion_perf.loc[best_emotion]
            else:
                best_emotion_rate = float('nan')
        except Exception as e:
            best_emotion = "N/A"
            best_emotion_rate = 0
            st.error(f"Error determining best emotion: {e}")

        try:
            best_politikfeld = politikfeld_perf.idxmax()
            if best_politikfeld in politikfeld_perf.index:
                best_politikfeld_rate = politikfeld_perf.loc[best_politikfeld]
            else:
                best_politikfeld_rate = float('nan')
        except Exception as e:
            best_politikfeld = "N/A"
            best_politikfeld_rate = 0
            st.error(f"Error determining best politikfeld: {e}")

        st.markdown(
            f"""
            ### Zusammenfassung:
            Die folgenden Textfelder zeigen automatisch die best performenden Sentimente, Emotionen und Politikfelder in der über die Filter auf der Seitenleiste ausgewählten Gruppen / Parteien. 
            Danach folgen jeweils die drei Posts mit der höchsten Interaktionsrate in den jeweiligen Kategorien. Für einen kompletten Überblick, über die Posts in der gefilterten Gruppe, können die generierten Tabellen weiter unten genutzt werden.
            - **Sentiment:** {best_sentiment} (Avg. Interaction Rate: {best_sentiment_rate:.2f})
            - **Emotion:** {best_emotion} (Avg. Interaction Rate: {best_emotion_rate:.2f})
            - **Politikfeld:** {best_politikfeld} (Avg. Interaction Rate: {best_politikfeld_rate:.2f})
            """
        )
    else:
        st.info("Not enough data to compute performance metrics for one or more categories.")
else:
    st.info("The 'Post-Interaktionsrate' column is not available to calculate performance metrics.")
#TEST ABOVE

#TEST2
# First, compute and clean the best-performing categories as before
# (Assuming best_sentiment, best_emotion, best_politikfeld have been computed,
#  and that filtered_data has been cleaned accordingly)

# For example, ensure that 'Post-Interaktionsrate' is numeric:
if 'Post-Interaktionsrate' in filtered_data.columns:
    filtered_data['Post-Interaktionsrate'] = pd.to_numeric(filtered_data['Post-Interaktionsrate'], errors='coerce')

# Compute the top posts for each category
top_sentiment_posts = filtered_data[filtered_data['sentiment'] == best_sentiment] \
    .sort_values(by='Post-Interaktionsrate', ascending=False).head(3)
top_emotion_posts = filtered_data[filtered_data['emotion'] == best_emotion] \
    .sort_values(by='Post-Interaktionsrate', ascending=False).head(3)
top_politikfeld_posts = filtered_data[filtered_data['politikfeld'] == best_politikfeld] \
    .sort_values(by='Post-Interaktionsrate', ascending=False).head(3)

# Create three columns to display the posts side by side
cols = st.columns(3)

with cols[0]:
    st.markdown(f"### Top posts für Sentiment '{best_sentiment}'")
    if not top_sentiment_posts.empty:
        for _, row in top_sentiment_posts.iterrows():
            st.markdown(f"*Interaction Rate:* {row['Post-Interaktionsrate']:.2f}")
            st.markdown(f"*Anzahl Likes:* {row['Anzahl Likes']:.2f}")
            st.write(row['Text'])
            st.write("---")
    else:
        st.write("No posts found for this sentiment.")

with cols[1]:
    st.markdown(f"### Top posts für Emotion '{best_emotion}'")
    if not top_emotion_posts.empty:
        for _, row in top_emotion_posts.iterrows():
            st.markdown(f"*Interaction Rate:* {row['Post-Interaktionsrate']:.2f}")
            st.markdown(f"*Anzahl Likes:* {row['Anzahl Likes']:.2f}")
            st.write(row['Text'])
            st.write("---")
    else:
        st.write("No posts found for this emotion.")

with cols[2]:
    st.markdown(f"### Top posts für Politikfeld '{best_politikfeld}'")
    if not top_politikfeld_posts.empty:
        for _, row in top_politikfeld_posts.iterrows():
            st.markdown(f"*Interaction Rate:* {row['Post-Interaktionsrate']:.2f}")
            st.markdown(f"*Anzahl Likes:* {row['Anzahl Likes']:.2f}")
            st.write(row['Text'])
            st.write("---")
    else:
        st.write("No posts found for this politikfeld.")

#END TEST2

# Debugging: Show the count of filtered rows
st.write("Number of rows after filtering:", len(filtered_data))

# Ensure Datum is correctly parsed and contains no NaT values
if filtered_data['Datum'].isna().sum() > 0:
    st.write("Warning: Some 'Datum' values could not be parsed. They are excluded from plots.")
    filtered_data = filtered_data.dropna(subset=['Datum'])




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
        st.line_chart(temp_data['Reaktionen, Kommentare & Shares'])

# Show interaction rate over time in the second column
with col4:
    st.write("### Interaction Rate Over Time")
    if not filtered_data.empty and 'Datum' in filtered_data.columns and 'Post-Interaktionsrate' in filtered_data.columns:
        # Make a copy to avoid modifying the original DataFrame
        temp_data = filtered_data.copy()
        temp_data.set_index('Datum', inplace=True)
        st.line_chart(temp_data['Post-Interaktionsrate'])

# Additional Visualizations

# Sentiment distribution
st.write("### Sentiment Distribution")
sentiment_counts = filtered_data['sentiment'].value_counts()
st.bar_chart(sentiment_counts)

# Ensure the columns for aggregation are numeric
numeric_columns = ['Anzahl Likes', 'Anzahl Kommentare', 'Reaktionen, Kommentare & Shares']
numeric_data = filtered_data[numeric_columns].apply(pd.to_numeric, errors='coerce')

# Adding sentiment back to numeric data for grouping
numeric_data['sentiment'] = filtered_data['sentiment']

# Using columns to display bar charts side-by-side
col5, col6 = st.columns(2)

# Average engagement by sentiment in the first column
with col5:
    st.write("### Average Likes by Sentiment")
    average_likes = numeric_data.groupby('sentiment')['Anzahl Likes'].mean()
    st.bar_chart(average_likes)

# Average engagement by sentiment in the second column
with col6:
    st.write("### Average Comments by Sentiment")
    average_comments = numeric_data.groupby('sentiment')['Anzahl Kommentare'].mean()
    st.bar_chart(average_comments)

# Display the first few rows of the data
st.write("## Data Preview")
st.dataframe(data.head())

# Display filtered data
st.write(f"## Filtered Data for Selected Profiles, Sentiments, Politikfeld, and Emotions")
st.dataframe(filtered_data)

# Sidebar selection for word cloud type
st.sidebar.title("Word Cloud Options")
wordcloud_option = st.sidebar.selectbox("Select Word Cloud Type", options=['sentiment', 'emotion', 'politikfeld'])

# Word Cloud for Text Analysis
st.write("### Word Cloud for Text Analysis by Selected Type")

# Generate and display word clouds based on the selected option
if wordcloud_option == 'sentiment':
    for sentiment in filtered_data['sentiment'].unique():
        sentiment_text = " ".join(filtered_data[filtered_data['sentiment'] == sentiment]['Text'])
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(sentiment_text)
        
        st.write(f"#### Word Cloud for {sentiment} Sentiment")
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        st.pyplot(plt)
        
elif wordcloud_option == 'emotion':
    for emotion in filtered_data['emotion'].unique():
        emotion_text = " ".join(filtered_data[filtered_data['emotion'] == emotion]['Text'])
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(emotion_text)
        
        st.write(f"#### Word Cloud for {emotion} Emotion")
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        st.pyplot(plt)
        
elif wordcloud_option == 'politikfeld':
    for politikfeld in filtered_data['politikfeld'].unique():
        politikfeld_text = " ".join(filtered_data[filtered_data['politikfeld'] == politikfeld]['Text'])
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(politikfeld_text)
        
        st.write(f"#### Word Cloud for {politikfeld} Politikfeld")
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        st.pyplot(plt)
