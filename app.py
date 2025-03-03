import streamlit as st
from bert_inference import get_prediction  # Make sure this module is correctly imported
from google.cloud import firestore
from streamlit_option_menu import option_menu
import pandas as pd

def get_db():
    return firestore.Client.from_service_account_json('key.json')

def save_classification(username, title, text_input, classification_type, result):
    if not username:
        raise ValueError("Username is required to save the classification.")

    db = get_db()
    classifications_ref = db.collection('users').document(username).collection('classifications')
    
    probability = float(result['probability']) if isinstance(result['probability'], (float, int)) else float(result['probability'])
    
    classification_data = {
        "title": title,
        "text": text_input,
        "type": classification_type,
        "result": {
            "sentiment": result['sentiment'],
            "probability": probability
        }
    }
    
    classifications_ref.add(classification_data)

def retrieve_classifications(username):
    db = get_db()
    classifications_ref = db.collection('users').document(username).collection('classifications')
    docs = classifications_ref.stream()
    classifications = [doc.to_dict() for doc in docs]
    return classifications

def generate_title(text):
    words = text.split()
    return " ".join(words[:2]) if len(words) >= 2 else "Untitled"

def clear_history(username):
    db = get_db()
    classifications_ref = db.collection('users').document(username).collection('classifications')
    docs = classifications_ref.stream()
    for doc in docs:
        doc.reference.delete()

def visualize_classifications_bar(classifications):
    sentiments = [classification['result']['sentiment'] for classification in classifications]
    sentiment_counts = pd.Series(sentiments).value_counts()
    
    sentiment_df = pd.DataFrame({
        'Sentiment': sentiment_counts.index,
        'Count': sentiment_counts.values
    }).set_index('Sentiment')
    
    sentiment_df['Color'] = sentiment_df.index.map({
        'Positive': 'green',
        'Negative': 'red'
    })
    
    st.subheader("Sentiment Analysis - Bar Chart")
    st.write("Bar chart showing counts of positive and negative sentiments.")
    st.bar_chart(sentiment_df['Count'], use_container_width=True)

def visualize_classifications_area(classifications):
    data = {'Title': [], 'Positive': [], 'Negative': []}
    
    for classification in classifications:
        sentiment = classification['result']['sentiment']
        probability = classification['result']['probability']
        data['Title'].append(classification['title'])
        data['Positive'].append(probability if sentiment == 'Positive' else 0)
        data['Negative'].append(-probability if sentiment == 'Negative' else 0)
    
    df = pd.DataFrame(data)
    df = df.groupby('Title').sum()
    
    st.subheader("Sentiment Analysis - Area Chart")
    st.write("Area chart showing positive and negative sentiment scores.")
    st.area_chart(df, use_container_width=True)

def classifier():
    st.set_page_config(page_title="Text Classification", page_icon=":pencil:", layout="wide")

    # Initialize session state variables if they don't exist
    if 'username' not in st.session_state:
        st.session_state.username = ''
    
    if 'classification_result' not in st.session_state:
        st.session_state.classification_result = None
    
    if 'show_history' not in st.session_state:
        st.session_state.show_history = False
    
    if 'selected_classification' not in st.session_state:
        st.session_state.selected_classification = None

    st.markdown("""<style>/* Add styles here */</style>""", unsafe_allow_html=True)

    menu = ["Home", "Classify Text", "About", "Log Out"]
    choice = option_menu(
        menu_title=None,
        options=menu,
        icons=['house', 'pencil', 'info-circle', 'logout'],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal"
    )

    # Manually set the username in local development
    if st.session_state.username == '':
        st.session_state.username = st.text_input("Enter Username", "")
    
    username = st.session_state.username

    # Handling Log Out
    if choice == "Log Out":
        st.session_state.pop('username', None)
        st.session_state.pop('selected_classification', None)
        st.session_state.pop('classification_result', None)
        st.session_state.pop('show_history', None)
        st.rerun()

    if not username:
        st.warning("Please enter your username.")
        return  # Exit early if no username is set

    st.sidebar.title("Text Classification")
    st.title("Text Classification App")
    st.markdown("Classify your text using AI-powered models.")

    with st.sidebar:
        st.subheader("History")
        if st.button("Clear History"):
            if username:
                clear_history(username)
                st.success("All history cleared.")
                st.rerun()
            else:
                st.warning("No user logged in.")
        if username:
            saved_classifications = retrieve_classifications(username)
            if saved_classifications:
                options = ["History!"] + [classification.get('title', 'Untitled') for classification in saved_classifications]
                selected_option = option_menu(
                    menu_title="",
                    options=options,
                    icons=['clock']+['file-earmark-text'] * len(options),
                    menu_icon="cast",
                    default_index=0,
                    orientation="vertical"
                )
                if selected_option == "History!":
                    st.session_state.selected_classification = None
                    st.session_state.show_history = False
                else:
                    for classification in saved_classifications:
                        if selected_option == classification.get('title', 'Untitled'):
                            st.session_state.selected_classification = classification
                            st.session_state.show_history = True
                            break
            else:
                st.write("No history available.")

    if choice == "Home":
        st.subheader(f"Welcome, {username}!")
        st.markdown("""This app allows you to classify text into different categories using machine learning.""")

        if username:
            saved_classifications = retrieve_classifications(username)
            if saved_classifications:
                col1, col2 = st.columns(2)
                
                with col1:
                    visualize_classifications_bar(saved_classifications)
                
                with col2:
                    visualize_classifications_area(saved_classifications)
            else:
                st.write("No classifications found.")
        else:
            st.write("Please log in to view your classifications.")

    elif choice == "Classify Text":
        st.subheader("Classify Text")
        text_input = st.text_area("Enter Text Here", "Type or paste your text here...")
        classification_type = st.selectbox("Classification Type", ["Sentiment Analysis", "Topic Categorization"])

        if st.button("Classify"):
            if classification_type == "Sentiment Analysis":
                result = get_prediction(text_input)
                title = generate_title(text_input)
                save_classification(username, title, text_input, classification_type, result)
                st.session_state.classification_result = result
                st.session_state.show_history = True
                st.rerun()

        if st.session_state.classification_result:
            result = st.session_state.classification_result
            if result:
                st.subheader("Latest Classification Result")
                if result['sentiment'] == 'Negative':
                    st.error(f"Sentiment: {result['sentiment']}, Probability: {result['probability']:.2f}")
                else:
                    st.success(f"Sentiment: {result['sentiment']}, Probability: {result['probability']:.2f}")

    elif choice == "About":
        st.subheader("About")
        st.markdown("""### About This App
            This app uses machine learning models to classify text into different categories.
            - **Sentiment Analysis**: Detects the sentiment of the text (Positive, Neutral, Negative).
            - **Topic Categorization**: Coming soon!""")

    if st.session_state.show_history and st.session_state.get('selected_classification'):
        classification = st.session_state.selected_classification
        st.subheader(f"Input and Output for '{classification.get('title', 'Untitled')}'")
        st.write(f"- Type: {classification['type']}")
        st.write(f"- Text: {classification['text']}")
        st.write(f"- Sentiment: {classification['result']['sentiment']}, Probability: {classification['result']['probability']:.2f}")

if __name__ == "__main__":
    classifier()
