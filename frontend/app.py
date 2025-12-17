import streamlit as st

st.set_page_config(
    page_title="Flatmate App",
    page_icon="🏠",
    layout="wide"
)

st.title("Welcome to the Flatmate App! 🏠")
st.markdown("Manage your shared living space with ease.")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("⚙️ Settings")
        st.write("Configure your house and user profile.")
        st.page_link("pages/0_Settings.py", label="Go to Settings", icon="⚙️")

with col2:
    with st.container(border=True):
        st.subheader("📅 Calendar")
        st.write("Schedule cleaning, events, and more.")
        st.page_link("pages/1_Calendar.py", label="Go to Calendar", icon="📅")

col3, col4 = st.columns(2)

with col3:
    with st.container(border=True):
        st.subheader("🛒 Shopping List")
        st.write("Keep track of what needs to be bought.")
        st.page_link("pages/2_Shopping_List.py", label="Go to Shopping List", icon="🛒")

with col4:
    with st.container(border=True):
        st.subheader("💸 Expenses")
        st.write("Split bills and see who owes what.")
        st.page_link("pages/3_Expenses.py", label="Go to Expenses", icon="💸")