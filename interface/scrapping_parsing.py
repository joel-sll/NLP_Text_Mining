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
    


# Function to simulate a popup for user input
def user_input_popup():
    # Display the button
    if st.button("Click to provide feedback"):
        # Show a text input field (like a popup)
        user_input = st.text_area("Please enter your feedback here:")

        if user_input:
            st.write(f"Your feedback: {user_input}")
        else:
            st.write("No feedback provided yet.")

# Call the function to display the button and pop-up input
user_input_popup()
