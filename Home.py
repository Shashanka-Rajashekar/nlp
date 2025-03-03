import streamlit as st
from streamlit_option_menu import option_menu
from login import login_page
from signin import signin_page
from app import classifier
from forgot import forgot
def main():
    if 'username' in st.session_state:
        classifier()
    else:
        with st.sidebar:
            selected = option_menu(
                menu_title="Welcome !",  
                options=["Login", "Create Account","Forgot Password ?"], 
                icons=["house", "envelope"],
                menu_icon="cast",  
                default_index=0,  
            )
        if selected == "Login":
            
            login_page()

        elif selected == "Create Account":
            signin_page()
        elif selected == "Forgot Password ?":
            forgot()

if __name__ == "__main__":
    main()
