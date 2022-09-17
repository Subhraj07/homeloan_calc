import streamlit as st
import extra_streamlit_components as stx
from base_calculator import get_base_calc
from custom_calculator import get_custom_base_calc

st.set_page_config(
    page_title = 'Home Loan Calculator',
    page_icon = '✅',
    layout = 'wide'
)

if 'months' not in st.session_state:
    st.session_state.months = 1
if 'amounts' not in st.session_state:
    st.session_state.amounts = []

chosen_id = stx.tab_bar(data=[
    stx.TabBarItemData(id=1, title="Base Calculator", description="Base EMI"),
    stx.TabBarItemData(id=2, title="Custom Calculator", description="EMI with Deposit money on certain interval"),
], default=1)

if chosen_id == str(1):
    get_base_calc()
if chosen_id == str(2):
    get_custom_base_calc()