#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 14:05:13 2025

@author: joannastewart
"""

import streamlit as st
import sim_processing as sp
import matplotlib.pyplot as plt

st.title("Optimizing Inventory at a Summertime Concession Stand")
st.write("Input your assumptions, hit submit, and review the scenarios below")


with st.form('Inputs'):
    n = st.slider('Number of simulations per inventory level',min_value=100,
                  max_value=5000,value=1000,step=100)
    st.write('The daily customers lower and upper bound define the range for 90% of a lognormal distribution. Lower needs to be less than upper.')
    c1, c2= st.columns(2)
    with c1:
        lower = st.number_input("Daily Customers Lower Bound",value=100,step=10)
        p = st.number_input("Percentage Hot Dogs",min_value=0.00,max_value=1.00,
                            value=.45,step=.05)
        price_hd = st.number_input("Price Hot Dog",min_value=5.00,max_value=12.00,
                            value=6.50,step=.50)
        cost_hd = st.number_input("Cost Hot Dog",min_value=1.00,max_value=6.00,
                            value=2.70,step=.10)
        shrink_hd = st.number_input("Storage Shrink Hot Dog",min_value=0.00,max_value=.30,
                            value=0.00,step=.05)
        badwill = st.number_input("Bad Will Factor",min_value = 0,max_value=10,
                                  value=4,step=1)
        st.write("If factor is 4, we assume 4 future transactions are lost due to bad will when customer is shorted")
        
    with c2:
        upper = st.number_input("Daily Customers Upper Bound",value=180,step=10)
        st.write(f"Percentage Hamburger is:")
        st.write(f"{1-p:.2f}")
        price_hb = st.number_input("Price Hamburger",min_value=5.00,max_value=12.00,
                            value=9.00,step=.50)
        cost_hb = st.number_input("Cost Hamburger",min_value=1.00,max_value=6.00,
                            value=4.20,step=.10)
        shrink_hb = st.number_input("Storage Shrink Hamburger",min_value=0.00,max_value=.30,
                            value=0.10,step=.05)
        meets = st.number_input("Number of Swim Meets (Multiperiod)",min_value = 1,max_value=10,
                                  value=6,step=1)
    submit = st.form_submit_button(label = 'Submit')

if submit:
    df = sp.multiperiod(n,lower,upper,p,price_hd,price_hb,cost_hd,cost_hb,
                    badwill,False,1,shrink_hd,shrink_hb)
    fig1 = sp.customer_histogram(df)
    best1, summ1 = sp.summarize(df)
    fig2 = sp.profit_histogram(df[df['Inv_Combo']==best1])
    
    dfpack = sp.multiperiod(n,lower,upper,p,price_hd,price_hb,cost_hd,cost_hb,
                    badwill,True,1,shrink_hd,shrink_hb)
    best2,summ2=sp.summarize(dfpack)
    fig3 = sp.profit_histogram(dfpack[dfpack['Inv_Combo']==best2])

    dfmulti = sp.multiperiod(n,lower,upper,p,price_hd,price_hb,cost_hd,cost_hb,
                    badwill,True,meets,shrink_hd,shrink_hb)
    best3,summ3=sp.summarize(dfmulti)
    fig4 = sp.profit_histogram(dfmulti[dfmulti['Inv_Combo']==best3])

    with st.container(key='Customer_Hist'):
        st.header('Daily Customer Distribution') 
        st.pyplot(fig1)
    
    with st.container(key='Scenario1'):
        st.header("Single Period, No Inventory Constraints") 
        st.subheader(f"Optimal Inventory: {summ1.iloc[0,0]} hot dogs and {summ1.iloc[0,1]} hamburgers, leading to revenue of \${summ1.iloc[0,3]:,.0f}, profit of \${summ1.iloc[0,4]:,.0f}, and unmet demand of {summ1.iloc[0,6]:.2%}")
        st.pyplot(fig2)
    
    with st.container(key='Scenario2'):
        st.header("Single Period, Inventory in Bulk Packs") 
        st.subheader(f"Optimal Inventory: {summ2.iloc[0,0]} hot dogs and {summ2.iloc[0,1]} hamburgers, leading to revenue of \${summ2.iloc[0,3]:,.0f}, profit of \${summ2.iloc[0,4]:,.0f}, and unmet demand of {summ2.iloc[0,6]:.2%}")
        st.pyplot(fig3)
        
    with st.container(key='Scenario3'):
        st.header("Multi Period, Inventory in Bulk Packs") 
        st.subheader(f"Optimal Inventory: {summ3.iloc[0,0]} hot dogs and {summ3.iloc[0,1]} hamburgers, leading to revenue of \${summ3.iloc[0,3]:,.0f}, profit of \${summ3.iloc[0,4]:,.0f}, and unmet demand of {summ3.iloc[0,6]:.2%}")
        st.write("Note: Revenue and Profit are average per meet in order to be comparable to the other scenarios")
        st.pyplot(fig4)
