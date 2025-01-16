import streamlit as st

def show_analyse_inter_restaurant():
    # Ajouter du CSS pour styliser le header
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
    
    # Titre avec le style appliqué
    st.markdown('<div class="header">Analyse Inter-Restaurant</div>', unsafe_allow_html=True)
    
    # Texte explicatif
    st.write("""
    Ici, vous pouvez effectuer des analyses au sein d'un même restaurant.
    """)
