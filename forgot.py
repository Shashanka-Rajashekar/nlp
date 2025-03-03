import streamlit as st
from google.cloud import firestore

def get_db():
    try:
        db = firestore.Client.from_service_account_json('key.json')
        return db
    except Exception as e:
        st.error(f"Failed to initialize Firestore client: {e}")
def verify_email_username(email, vusername):
    try:
        db = get_db()
        auser = db.collection('users')
        query = auser.where('username', '==', vusername).where('email_id', '==', email).limit(1).get()
        return len(query) == 1
    except Exception as e:
        st.error(f"Failed to verify email and username: {e}")

def update_password(username, new_password):
    try:
        db = get_db()
        auser = db.collection('users')
        user_ref = auser.document(username)
        user_ref.update({"password": new_password})
        st.write(f"Password updated for user: {username}")  # Debug line
    except Exception as e:
        st.error(f"Failed to update password: {e}")
def forgot():
            st.title("Forgot Password")
            st.header("Reset Password")

            with st.form("forgot_password_form"):
                email = st.text_input("Enter your email")
                vusername = st.text_input("Enter your username for verification")
                new_password = st.text_input("Enter new password", type='password')
                submit_ = st.form_submit_button("Submit")

                if submit_:
                    if verify_email_username(email, vusername):
                        st.write(f"Attempting to update password for user: {vusername}")  # Debug line
                        update_password(vusername, new_password)
                        st.success("Password updated successfully!")
                        st.info("You can now [login](#) with your new password.")
                    else:
                        st.warning("Email and username do not match")
                        
if __name__ == "__main__":
    forgot()