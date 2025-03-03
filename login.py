import streamlit as st
from google.cloud import firestore
from signin import signin_page

# Function to initialize Firestore client
def get_db():
    db = firestore.Client.from_service_account_json('key.json')
    return db


def authenticate(username, password):
    try:
        db = get_db()
        auser = db.collection('users')
        query = auser.where('username', '==', username).limit(1).get()
        if query:
            user_doc = query[0]
            user_data = user_doc.to_dict()
            return user_data.get('password') == password
        return False
    except Exception as e:
        st.error(f"Authentication failed: {e}")

def usernotexist(username):
    try:
        db = get_db()
        auser = db.collection('users')
        query = auser.where('username', '==', username).get()
        return len(query) == 0
    except Exception as e:
        st.error(f"Failed to check if user exists: {e}")


def login_page():
        st.title("Text Classification")
        st.header("Login")

        with st.form("login_form"):
            username = st.text_input("Enter your username")
            password = st.text_input("Enter the password", type='password')
            
            submit_button = st.form_submit_button("Submit")

            if submit_button:
                if usernotexist(username):
                    st.warning("User doesn't exist")
                elif authenticate(username, password):
                    st.success("Login successful")
                    st.session_state['username'] = username
                    st.session_state['page'] = 'home'
                    st.experimental_rerun()  # Redirect to the main page
                else:
                    st.warning("Incorrect password")

        st.markdown("Forgot Password? [click the 'Create Account' option in the sidebar]()")

        st.markdown("Don't have an account? [click the 'Create Account' option in the sidebar]()")

if __name__ == "__main__":
    login_page()
