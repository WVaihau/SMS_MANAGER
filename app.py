import controller as ctrl
import streamlit as st


def main():

    authenticator = ctrl.auth_usr()

    name, authentication_status, username = authenticator.login(
        'Login', 'main')

    if st.session_state["authentication_status"]:
        ctrl.csv_uploader(authenticator)

    elif st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')


if __name__ == "__main__":
    main()
