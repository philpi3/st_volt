import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# --- Load and Preprocess Data ---
data = pd.read_csv("pages/data/Jan25-04.02.csv")

# Normalize columns by stripping extra quotes and whitespace
data['sentiment'] = data['sentiment'].str.strip(" '")
data['politikfeld'] = data['politikfeld'].str.strip(" '")
data['emotion'] = data['emotion'].str.strip(" '")
data.columns = data.columns.str.strip()

# Convert columns to numeric (removing commas)
data['Anzahl Likes'] = data['Anzahl Likes'].str.replace(',', '').astype(float)
data['Anzahl Kommentare'] = data['Anzahl Kommentare'].str.replace(',', '').astype(float)
data['Reaktionen, Kommentare & Shares'] = data['Reaktionen, Kommentare & Shares'].str.replace(',', '').astype(float)
data['Post-Interaktionsrate'] = data['Post-Interaktionsrate'].str.replace(',', '.').astype(float)

# Convert 'Datum' to datetime (replace commas with space)
data['Datum'] = data['Datum'].str.replace(',', ' ')
data['Datum'] = pd.to_datetime(data['Datum'], format='%d.%m.%y %H:%M', errors='coerce')

# --- Sidebar Filters ---
st.sidebar.title("Filter Options")

# Group filter
groups = data['Gruppe'].unique()
groups_list = st.sidebar.multiselect("Select Group", options=['All'] + list(groups), default=['All'])
selected_groups = groups if 'All' in groups_list else groups_list

# Profile filter
profiles = data['Profil'].unique()
profiles_list = st.sidebar.multiselect("Select Profiles", options=['All'] + list(profiles), default=['All'])
selected_profiles = profiles if 'All' in profiles_list else profiles_list

# Sentiment filter
sentiments = data['sentiment'].unique()
sentiments_list = st.sidebar.multiselect("Select Sentiments", options=['All'] + list(sentiments), default=['All'])
selected_sentiments = sentiments if 'All' in sentiments_list else sentiments_list

# Politikfeld filter
politikfelds = data['politikfeld'].unique()
politikfeld_list = st.sidebar.multiselect("Select Politikfeld", options=['All'] + list(politikfelds), default=['All'])
selected_politikfeld = politikfelds if 'All' in politikfeld_list else politikfeld_list

# Emotion filter
emotions = data['emotion'].unique()
emotions_list = st.sidebar.multiselect("Select Emotions", options=['All'] + list(emotions), default=['All'])
selected_emotions = emotions if 'All' in emotions_list else emotions_list

# Text search filter
phrase = st.sidebar.text_input("Enter a phrase to search in Text", value="")

# Filter the data based on selections
filtered_data = data[
    (data['Profil'].isin(selected_profiles)) &
    (data['sentiment'].isin(selected_sentiments)) &
    (data['politikfeld'].isin(selected_politikfeld)) &
    (data['emotion'].isin(selected_emotions)) &
    (data['Gruppe'].isin(selected_groups))
]

if phrase:
    filtered_data = filtered_data[filtered_data['Text'].str.contains(phrase, case=False, na=False)]

st.markdown("WORK IN PROGRESS - Hier teste ich neue Visualisierungen/Plots/Wordclouds/Maps mit Plotly, anstelle der weniger leistungsstarken streamlit lösung auf der Instagram 2025 Seite. Wenn ich hier fertig bin, wird plotly auch auf der Hauptseite eingebunden.")

# --- Performance Metrics (existing logic) ---
if 'Post-Interaktionsrate' in filtered_data.columns:
    filtered_data['Post-Interaktionsrate'] = pd.to_numeric(filtered_data['Post-Interaktionsrate'], errors='coerce')
    sentiment_perf = filtered_data.groupby('sentiment')['Post-Interaktionsrate'].mean()
    emotion_perf = filtered_data.groupby('emotion')['Post-Interaktionsrate'].mean()
    politikfeld_perf = filtered_data.groupby('politikfeld')['Post-Interaktionsrate'].mean()

    if not sentiment_perf.empty and not emotion_perf.empty and not politikfeld_perf.empty:
        try:
            best_sentiment = sentiment_perf.idxmax()
            best_sentiment_rate = sentiment_perf.loc[best_sentiment]
        except Exception as e:
            best_sentiment = "N/A"
            best_sentiment_rate = 0
            st.error(f"Error determining best sentiment: {e}")
        try:
            best_emotion = emotion_perf.idxmax()
            best_emotion_rate = emotion_perf.loc[best_emotion]
        except Exception as e:
            best_emotion = "N/A"
            best_emotion_rate = 0
            st.error(f"Error determining best emotion: {e}")
        try:
            best_politikfeld = politikfeld_perf.idxmax()
            best_politikfeld_rate = politikfeld_perf.loc[best_politikfeld]
        except Exception as e:
            best_politikfeld = "N/A"
            best_politikfeld_rate = 0
            st.error(f"Error determining best politikfeld: {e}")

        st.markdown(
            f"""
            ### Zusammenfassung:
            - **Sentiment:** {best_sentiment} (Avg. Interaction Rate: {best_sentiment_rate:.2f})
            - **Emotion:** {best_emotion} (Avg. Interaction Rate: {best_emotion_rate:.2f})
            - **Politikfeld:** {best_politikfeld} (Avg. Interaction Rate: {best_politikfeld_rate:.2f})
            """
        )
    else:
        st.info("Not enough data to compute performance metrics for one or more categories.")
else:
    st.info("The 'Post-Interaktionsrate' column is not available to calculate performance metrics.")

# --- Top Posts Display (existing logic) ---
if 'Post-Interaktionsrate' in filtered_data.columns:
    filtered_data['Post-Interaktionsrate'] = pd.to_numeric(filtered_data['Post-Interaktionsrate'], errors='coerce')

top_sentiment_posts = filtered_data[filtered_data['sentiment'] == best_sentiment] \
    .sort_values(by='Post-Interaktionsrate', ascending=False).head(3)
top_emotion_posts = filtered_data[filtered_data['emotion'] == best_emotion] \
    .sort_values(by='Post-Interaktionsrate', ascending=False).head(3)
top_politikfeld_posts = filtered_data[filtered_data['politikfeld'] == best_politikfeld] \
    .sort_values(by='Post-Interaktionsrate', ascending=False).head(3)

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

st.write("Number of rows after filtering:", len(filtered_data))
if filtered_data['Datum'].isna().sum() > 0:
    st.write("Warning: Some 'Datum' values could not be parsed. They are excluded from plots.")
    filtered_data = filtered_data.dropna(subset=['Datum'])

# --- Create Aggregated Daily Data for Plotly Charts ---
# Convert Datum to datetime (if not already) and create a 'Date' column for daily aggregation
filtered_data['Datum'] = pd.to_datetime(filtered_data['Datum'])
daily_data = filtered_data.copy()
daily_data['Date'] = daily_data['Datum'].dt.date

# Aggregate daily metrics (using the mean for demonstration)
daily_data = daily_data.groupby('Date').agg({
    'Anzahl Likes': 'mean',
    'Anzahl Kommentare': 'mean',
    'Reaktionen, Kommentare & Shares': 'mean',
    'Post-Interaktionsrate': 'mean'
}).reset_index()

# Optional: Create a rolling average for smoothing (e.g., 7-day window)
daily_data['Likes_Rolling'] = daily_data['Anzahl Likes'].rolling(window=7).mean()

# --- Plotly Visualizations ---
st.write("## Visualizations with Plotly")

# 1. Daily Average Likes Over Time (Line Chart without markers)
if not daily_data.empty:
    fig_likes = px.line(
        daily_data,
        x='Date',
        y='Anzahl Likes',
        title='Daily Average Likes Over Time',
        labels={'Date': 'Date', 'Anzahl Likes': 'Average Likes'}
    )
    st.plotly_chart(fig_likes, use_container_width=True)

# 2. Daily Average Comments Over Time (Line Chart)
if not daily_data.empty:
    fig_comments = px.line(
        daily_data,
        x='Date',
        y='Anzahl Kommentare',
        title='Daily Average Comments Over Time',
        labels={'Date': 'Date', 'Anzahl Kommentare': 'Average Comments'}
    )
    st.plotly_chart(fig_comments, use_container_width=True)

# 3. Dual-Axis Chart for Daily Average Likes and Comments
if not daily_data.empty:
    fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
    fig_dual.add_trace(
        go.Scatter(
            x=daily_data['Date'],
            y=daily_data['Anzahl Likes'],
            name="Likes",
            mode="lines",
            line=dict(color='blue', width=2),
            opacity=0.8
        ),
        secondary_y=False
    )
    fig_dual.add_trace(
        go.Scatter(
            x=daily_data['Date'],
            y=daily_data['Anzahl Kommentare'],
            name="Comments",
            mode="lines",
            line=dict(color='red', width=2),
            opacity=0.8
        ),
        secondary_y=True
    )
    fig_dual.update_layout(
        title_text="Daily Average Likes and Comments Over Time",
        xaxis_title="Date",
        legend=dict(orientation="h", x=0, y=-0.2)
    )
    fig_dual.update_yaxes(title_text="Average Likes", secondary_y=False)
    fig_dual.update_yaxes(title_text="Average Comments", secondary_y=True)
    st.plotly_chart(fig_dual, use_container_width=True)

# 4. Rolling Average of Likes (7-Day Rolling Average)
if not daily_data.empty:
    fig_roll = px.line(
        daily_data,
        x='Date',
        y='Likes_Rolling',
        title='7-Day Rolling Average of Likes',
        labels={'Date': 'Date', 'Likes_Rolling': '7-Day Avg Likes'}
    )
    st.plotly_chart(fig_roll, use_container_width=True)

# 5. Likes Over Time by Gruppe (Raw data; color-coded by Gruppe)
if not filtered_data.empty:
    fig_group = px.line(
        filtered_data,
        x='Datum',
        y='Anzahl Likes',
        color='Gruppe',
        title='Likes Over Time by Gruppe',
        labels={'Datum': 'Date', 'Anzahl Likes': 'Likes'}
    )
    st.plotly_chart(fig_group, use_container_width=True)

# 6. Sentiment Distribution (Bar Chart)
if 'sentiment' in filtered_data.columns:
    sentiment_counts = filtered_data['sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['sentiment', 'count']
    fig_sentiment = px.bar(
        sentiment_counts,
        x='sentiment',
        y='count',
        title="Sentiment Distribution",
        labels={'sentiment': 'Sentiment', 'count': 'Number of Posts'},
        color='sentiment'
    )
    st.plotly_chart(fig_sentiment, use_container_width=True)

# --- Word Cloud Section (existing logic) ---
st.sidebar.title("Word Cloud Options")
wordcloud_option = st.sidebar.selectbox("Select Word Cloud Type", options=['sentiment', 'emotion', 'politikfeld'])

st.write("### Word Cloud for Text Analysis by Selected Type")
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

# --- Data Preview ---
st.write("## Data Preview")
st.dataframe(data.head())
st.write("## Filtered Data for Selected Profiles, Sentiments, Politikfeld, and Emotions")
st.dataframe(filtered_data)
