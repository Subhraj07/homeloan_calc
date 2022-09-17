"""
import packages
"""
import sys
import os
import pandas as pd
import streamlit as st
from io import BytesIO
import numpy_financial as npf
import extra_streamlit_components as stx
from pyxlsb import open_workbook as open_xlsb


pd.set_option('display.float_format', lambda x: '%.3f' % x)

st.set_page_config(
    page_title = 'Home Loan Calculator',
    page_icon = '✅',
    layout = 'wide'
)

if 'months' not in st.session_state:
    st.session_state.months = 1
if 'amounts' not in st.session_state:
    st.session_state.amounts = []


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def isint(num):
    try:
        int(num)
        return True
    except ValueError:
        return False


def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data


def get_base_calc():
    principal_amount = st.text_input('Loan Amount', '10626000')
    interest_rate = st.text_input('Interest Rate', '8.1')
    repayment_yrs = st.selectbox(
        'Select Tenature Years for your Loan amount',
        ('5','10','15', '20', '25'))

    try:

        if not isint(principal_amount):
            raise ValueError('Loan Amount Should be a number')

        if not isfloat(interest_rate):
            raise ValueError('Interest Rate Should be a number')
        
        monthly_rate = float(interest_rate) / 100 / 12
        time_dur = int(repayment_yrs) * 12

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Loan Amount", int(principal_amount))
        col2.metric("Interest Rate", float(interest_rate))
        col3.metric("Tenature Years", int(repayment_yrs))
        col4.metric("Monthly Interest Rate", round(float(monthly_rate), 4))
        col5.metric("Total Duration(in Months)", float(time_dur))

        df = pd.DataFrame()

        df["month"] = range(1,int(repayment_yrs) * 12 + 1)

        df["monthly_principal_amount"] = df["month"].apply(lambda x: npf.ppmt(monthly_rate, x, time_dur, int(principal_amount))).abs()
        df["monthly_interest"] = df["month"].apply(lambda x: npf.ipmt(monthly_rate, x, time_dur, int(principal_amount))).abs()
        df["monthly_installment"] = df.apply(lambda x: (x["monthly_principal_amount"] + x["monthly_interest"]), axis=1).abs()


        global cur_val 
        cur_val = int(principal_amount)

        def get_value(abs_val):
            global cur_val
            cur_val = cur_val - abs_val
            return cur_val

        df["principal_amount"] = df["monthly_principal_amount"].apply(
            lambda x: get_value(x)
        )

        if st.button('Submit'):
            st.dataframe(df)

            col1, col2 = st.columns(2)
            col1.metric("Total Interest Paid", round(df["monthly_interest"].sum(),2))
            col2.metric("Total Paid", round(df["monthly_installment"].sum(),2))

            df_xlsx = to_excel(df)
            st.download_button(label='📥 Download',
                                    data=df_xlsx ,
                                    file_name= 'home_loan_emi_calculator.xlsx')

    except Exception as e:
        st.error(str(e), icon="🚨")


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


def get_custom_base_calc():
    principal_amount = st.text_input('Loan Amount', '10626000')
    interest_rate = st.text_input('Interest Rate', '8.1')
    repayment_yrs = st.selectbox(
        'Select Tenature Years for your Loan amount',
        ('5','10','15', '20', '25'))
    
    min_part_payment = st.text_input('Minimum Amount of Partpayment', '100000')

    data = {
        "months" : [],
        "amounts" : []
    }

    # try:

    if not isint(principal_amount):
        raise ValueError('Loan Amount Should be a number')

    if not isfloat(interest_rate):
        raise ValueError('Interest Rate Should be a number')
    
    if not isfloat(interest_rate):
        raise ValueError('Minimum Amount of Partpayment Should be a number')
    
    monthly_rate = float(interest_rate) / 100 / 12
    time_dur = int(repayment_yrs) * 12

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Loan Amount", int(principal_amount))
    col2.metric("Interest Rate", float(interest_rate))
    col3.metric("Tenature Years", int(repayment_yrs))
    col4.metric("Monthly Interest Rate", round(float(monthly_rate), 4))
    col5.metric("Total Duration(in Months)", float(time_dur))

    part_pay_df = part_payment_calc(time_dur, int(min_part_payment), int(int(principal_amount) * 0.25))
    data["months"] = list(part_pay_df.to_dict()["months"].values())
    data["amounts"] = list(part_pay_df.to_dict()["amounts"].values())

    custom_month_payment = dict(zip(*data.values()))

    df = pd.DataFrame()
    
    custom_month_payment_amounts = custom_month_payment.keys()

    def get_custom_month_payment(amount):
        if amount not in custom_month_payment_amounts:
            return 0
        return custom_month_payment[amount]

    df["month"] = range(1, int(repayment_yrs) * 12 + 1)
    df["advanced_payment"] = df["month"].apply(lambda x: get_custom_month_payment(x))
    df["monthly_principal_amount"] = df.apply(
        lambda x: (x["advanced_payment"] - npf.ppmt(monthly_rate, x["month"], time_dur, int(principal_amount))), axis=1
    ).abs()
    df["monthly_interest"] = df["month"].apply(lambda x: npf.ipmt(monthly_rate, x, time_dur, int(principal_amount))).abs()
    df["monthly_installment"] = df.apply(lambda x: (x["monthly_principal_amount"] + x["monthly_interest"]), axis=1).abs()

    global cur_val 
    cur_val = int(principal_amount)

    def get_value(abs_val):
        global cur_val
        cur_val = cur_val - abs_val
        return cur_val

    df["principal_amount"] = df["monthly_principal_amount"].apply(
        lambda x: get_value(x)
    )

    df = df[(df >= 0).all(1)]
    st.dataframe(df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Interest Paid", round(df["monthly_interest"].sum(),2))
    col2.metric("Total Paid", round(df["monthly_installment"].sum(),2))
    col3.metric(
        "Final Pending Amount (Less than montly EMI)", 
        round(
            (df["monthly_installment"].to_list()[-1] - df["principal_amount"].to_list()[-1]),
            2
        )
    )
    col4.metric("Total time taken to repay the loan (in months)",  len(df) + 1 )

    df_xlsx = to_excel(df)
    st.download_button(label='📥 Download',
                            data=df_xlsx ,
                            file_name= 'home_loan_custom_emi_calculator.xlsx')

chosen_id = stx.tab_bar(data=[
    stx.TabBarItemData(id=1, title="Base Calculator", description="Base EMI"),
    stx.TabBarItemData(id=2, title="Custom Calculator", description="EMI with Deposit money on certain interval"),
], default=1)

if chosen_id == str(1):
    get_base_calc()
if chosen_id == str(2):
    get_custom_base_calc()