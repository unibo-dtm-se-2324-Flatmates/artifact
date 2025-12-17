import requests
import streamlit as st

API_URL = "http://localhost:8000"

def render_sidebar():
    with st.sidebar:
        st.title("🏠 Flatmate Manager")
        
        st.markdown("---")
        
        # Custom Navigation
        st.subheader("Navigation")
        st.page_link("app.py", label="Home", icon="🏠")
        st.page_link("pages/0_Settings.py", label="Settings", icon="⚙️")
        st.page_link("pages/1_Calendar.py", label="Calendar", icon="📅")
        st.page_link("pages/2_Shopping_List.py", label="Shopping List", icon="🛒")
        st.page_link("pages/3_Expenses.py", label="Expenses", icon="💸")
        
        st.markdown("---")

    # Hide default navigation
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)

def get_events():
    try:
        response = requests.get(f"{API_URL}/calendar/")
        if response.status_code == 200:
            return response.json()
    except:
        return []
    return []

def create_event(event_data):
    requests.post(f"{API_URL}/calendar/", json=event_data)

def update_event(event_id, event_data):
    requests.put(f"{API_URL}/calendar/{event_id}", json=event_data)

def get_shopping_list():
    try:
        response = requests.get(f"{API_URL}/shopping/")
        if response.status_code == 200:
            return response.json()
    except:
        return []
    return []

def add_shopping_item(item_data):
    requests.post(f"{API_URL}/shopping/", json=item_data)

def remove_shopping_item(item_id):
    requests.delete(f"{API_URL}/shopping/{item_id}")

def get_expenses():
    try:
        response = requests.get(f"{API_URL}/expenses/")
        if response.status_code == 200:
            return response.json()
    except:
        return []
    return []

def add_expense(expense_data):
    requests.post(f"{API_URL}/expenses/", json=expense_data)

def get_debts():
    try:
        response = requests.get(f"{API_URL}/expenses/debts")
        if response.status_code == 200:
            return response.json()
    except:
        return []
    return []

def get_house_settings():
    try:
        response = requests.get(f"{API_URL}/house/")
        if response.status_code == 200:
            return response.json()
    except:
        return {"name": "My Flat", "flatmates": []}
    return {"name": "My Flat", "flatmates": []}

def update_house_settings(settings):
    requests.post(f"{API_URL}/house/", json=settings)

def get_reimbursements():
    try:
        response = requests.get(f"{API_URL}/expenses/reimbursements")
        if response.status_code == 200:
            return response.json()
    except:
        return []
    return []


def add_reimbursement(reimbursement_data):
    requests.post(f"{API_URL}/expenses/reimbursements", json=reimbursement_data)
