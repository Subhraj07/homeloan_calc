import streamlit as st
import pandas as pd

if 'months' not in st.session_state:
    st.session_state.months = 1
if 'amounts' not in st.session_state:
    st.session_state.amounts = []


class PartPatment:
    def __init__(self, page_id, time_dur, min_part_payment, max_part_payment):
        self.months = st.selectbox(
                            'Select years to pay the amount',
                            tuple(range(1, int(time_dur / 12) + 1 ))
                        )
        self.amounts = st.selectbox(
                            'Select Amount to Pay',
                            tuple(range(min_part_payment, max_part_payment, min_part_payment * 2))
                        )
    

def part_payment_calc(time_dur, min_part_payment, max_part_payment):
    placeholder = st.empty()
    placeholder2 = st.empty()

    while True:    
        months = st.session_state.months

        if placeholder2.button('submit', key=months):
            placeholder2.empty()
            df = pd.DataFrame(st.session_state.amounts)
            return df
            break
        else:        
            with placeholder.form(key=str(months)):
                part_pay = PartPatment(page_id=months, time_dur=time_dur, min_part_payment=min_part_payment, max_part_payment=max_part_payment)        

                if st.form_submit_button('Add Part Payment'):                
                    st.session_state.amounts.append({
                        'months': part_pay.months * 12, 'amounts': part_pay.amounts})
                    st.session_state.months += 1
                    df = pd.DataFrame(st.session_state.amounts)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.dataframe(df)
                    col2.metric("Total amount paid", int(df['amounts'].sum()))                    
                    placeholder.empty()
                    placeholder2.empty()
                else:
                    st.stop()