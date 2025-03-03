import streamlit as st
from google.cloud import firestore

def get_db():
    db = firestore.Client.from_service_account_json('key.json')
    return db

def unique(username):
    db = get_db()
    duser = db.collection('users')
    check = duser.where('username', '==', username).limit(1).get()
    return len(check) == 1

def signin_page():
    st.title("Text Classification")
    st.header("Create Account:")

    # Create a form for user signup
    with st.form("signup_form"):
        name = st.text_input("Enter your name")
        username = st.text_input("Enter username")
        email_id = st.text_input("Enter your Email Id")
        password = st.text_input("Enter the password", type='password')
        age = st.number_input("Enter your Age", step=1, format="%d")
        
        submit_button = st.form_submit_button("Submit")
        
        if submit_button:
            if len(username) <= 6:
                st.warning('Username must have a minimum of 6 characters', icon="⚠️")
            elif len(password) <= 6:
                st.warning('Password must have a minimum of 6 characters', icon="⚠️")
            elif '@' not in email_id:
                st.warning('Invalid email address. Please enter a valid email.', icon="⚠️")
            elif '.' not in email_id:
                st.warning('Invalid email address. Please enter a valid email.', icon="⚠️")
            elif unique(username):
                st.warning('User Exists', icon="⚠️")
            else:
                db = get_db()
                user_data = {
                    "name": name,
                    "username": username,
                    "email_id": email_id,
                    "password": password,
                    "age": age
                }
                users_ref = db.collection('users')
                users_ref.document(username).set(user_data)
                st.success("Account created successfully!")
                st.info("Account exists? [Click here to login](#Login)")

if __name__ == "__main__":
    signin_page()
