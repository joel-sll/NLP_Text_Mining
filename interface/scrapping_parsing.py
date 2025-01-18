import streamlit as st

def show_scrapping():

    st.markdown("""
        <style>
            .header {
                background-color: #00e19f;
                font-family: "New Icon";
                padding: 10px;
                text-align: center;
                border-radius: 10px;
                color: white;
                font-size: 25px;
                font-weight: bold;
            }
        </style>
    """, unsafe_allow_html=True)   

    st.markdown('<div class="header">Scrapping et Parsing</div>', unsafe_allow_html=True)