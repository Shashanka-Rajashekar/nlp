import streamlit as st
import pandas as pd
import plotly.express as px
from textblob import TextBlob

def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"

# Streamlit UI
st.title("Sentiment Analysis App")

# Text input for sentiment analysis
user_input = st.text_area("Enter text for analysis:")

if st.button("Analyze"):
    if user_input:
        sentiment = analyze_sentiment(user_input)
        st.write(f"Sentiment: {sentiment}")
    else:
        st.warning("Please enter some text for analysis.")

# File upload section for bulk sentiment analysis
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    if 'text' in df.columns:
        df['Sentiment'] = df['text'].apply(analyze_sentiment)
        st.write(df)
        
        # Sentiment count visualization
        sentiment_counts = df['Sentiment'].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']
        fig_bar = px.bar(sentiment_counts, x='Sentiment', y='Count', title='Sentiment Count', color='Sentiment')
        st.plotly_chart(fig_bar)
        
        fig_area = px.area(sentiment_counts, x='Sentiment', y='Count', title='Sentiment Distribution', color='Sentiment')
        st.plotly_chart(fig_area)
    else:
        st.error("CSV file must contain a 'text' column.")
