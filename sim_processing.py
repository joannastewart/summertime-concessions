#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 11:57:06 2025

@author: joannastewart
"""

import numpy as np
import pandas as pd
from scipy.stats import norm
import seaborn as sns
import matplotlib.pyplot as plt
np.random.seed(4)


def multiperiod(n,lower,upper,p,price_hd,price_hb,cost_hd,cost_hb,badwill,costco,meets,shrink_hd,shrink_hb):
    min_hd_storage = 12
    min_hb_storage = 1
    confidence = .9
    z = -norm.ppf((1-confidence)/2)
    sigma = np.log((upper/lower))/2/z
    mu = np.log(upper)-z*sigma
    hd_pack = 36
    hb_pack = 24
    if costco:
        low_range = 1
        high_range =int(upper*.8/24)
        range_hd = np.arange(low_range*hd_pack,high_range*hd_pack,hd_pack)
        range_hb = np.arange(low_range*hb_pack,high_range*hb_pack,hb_pack)
    else:
        low_range = int(((min(p,1-p)*lower)//5)*5)
        high_range =int(((upper*.8)//5)*5)
        range_hd = np.arange(low_range,high_range,5)
        range_hb = np.arange(low_range,high_range,5)
    badwill_hd = badwill*(price_hd-cost_hd)
    badwill_hb = badwill*(price_hb-cost_hb)
    results = []
    for inv_hd in range_hd:
        for inv_hb in range_hb:
            for _ in range(n):
                current_inv_hd = inv_hd
                current_inv_hb = inv_hb
                revenue = 0
                profit = 0
                tot_customers = 0
                unmet_customers = 0
                for meet in range(meets):
                    customers = np.random.lognormal(mean=mu, sigma=sigma, size=1)
                    customers = int(np.round(customers[0]))
                    demand_hd = np.random.binomial(n=customers,p=p)
                    demand_hb = customers - demand_hd
            
                    if demand_hd <= current_inv_hd:
                        sold_hd = demand_hd
                        unsold_hd = current_inv_hd - sold_hd
                        unmet_hd = 0
                    else:
                        sold_hd = current_inv_hd
                        unsold_hd = 0
                        unmet_hd = demand_hd - current_inv_hd
                    if demand_hb <= current_inv_hb:
                        sold_hb = demand_hb
                        unsold_hb = current_inv_hb - sold_hb
                        unmet_hb = 0
                    else:
                       sold_hb = current_inv_hb
                       unsold_hb = 0
                       unmet_hb = demand_hb-current_inv_hb

                    hd_stored = round((1-shrink_hd)*(unsold_hd // min_hd_storage) * min_hd_storage,0)
                    hd_wasted = unsold_hd - hd_stored
                    hb_stored = round((1-shrink_hb)*(unsold_hb // min_hb_storage) * min_hb_storage,0)
                    hb_wasted = unsold_hb - hb_stored
                
                    sales = (sold_hd*price_hd+sold_hb*price_hb)
                    prod_cogs =cost_hd*(sold_hd+hd_wasted)+cost_hb*(sold_hb+hb_wasted)
                    bad_will = unmet_hd*badwill_hd+unmet_hb*badwill_hb
                    prof = sales - prod_cogs - bad_will
                
                    revenue += sales
                    profit += prof
                    tot_customers+= customers
                    unmet_customers += (unmet_hd+unmet_hb)

                    if hd_stored >=inv_hd:
                        current_inv_hd = hd_stored
                    else:
                        current_inv_hd = inv_hd + hd_stored % hd_pack
                    if hb_stored >=inv_hb:
                        current_inv_hb = hb_stored
                    else:
                        current_inv_hb = inv_hb + hb_stored % hb_pack
                
            
            
                profit -= (hd_stored*cost_hd+hb_stored*cost_hb)
                combo = str(inv_hd) + "_" + str(inv_hb)
                    
                results.append({
                'Inv_HD': inv_hd,
                'Inv_HB': inv_hb,
                'Inv_Combo':combo,
                'Customers': tot_customers,
                'Unmet_Customers':unmet_customers,
                'Revenue':revenue/meets,
                'Profit':profit/meets
                })
    df = pd.DataFrame(results) 
    return df
    
def customer_histogram(df):
    customers_mean = df['Customers'].mean()
    fig, ax = plt.subplots()
    sns.histplot(data=df, x='Customers', ax=ax)
    ax.axvline(customers_mean, color='red', linestyle='dashed', linewidth=1, label=f"Mean {customers_mean:.1f}")
    ax.set_title('Customer Demand')
    ax.legend()
    return fig

def profit_histogram(df):
    profit_mean = df['Profit'].mean()
    fig, ax = plt.subplots()
    sns.histplot(data=df, x='Profit', ax=ax)
    ax.axvline(profit_mean, color='red', linestyle='dashed', linewidth=1, label=f"Mean {profit_mean:.0f}")
    ax.set_title('Profit Distribution Across Simulations')
    ax.legend()
    return fig

def summarize(df):
    df_summ = df.groupby(['Inv_HD', 'Inv_HB','Inv_Combo']).agg(
        Customers = ('Customers','sum'),
        Unmet_Customers = ('Unmet_Customers','sum'),
        Revenue = ('Revenue','mean'),
        Profit = ('Profit','mean'),
        Profit_StDev = ('Profit','std')
        ).reset_index()
    df_summ['Pct_Unmet']=df_summ['Unmet_Customers']/df_summ['Customers']
    df_summ.drop(columns=['Customers','Unmet_Customers'],inplace=True)
    df_summ.sort_values(by='Profit',ascending=False,inplace=True)
    best = df_summ.iloc[0,2]
    return best, df_summ[0:5]

n=5000
df = multiperiod(n,100,180,.45,6.5,9.0,2.68,4.21,4,False,1,0.0,0)
fig1 = customer_histogram(df)
plt.show()
best1, summ1 = summarize(df)
print(summ1)
fig2 = profit_histogram(df[df['Inv_Combo']==best1])
plt.show()

dfpack = multiperiod(n,100,180,.45,6.5,9.0,2.68,4.21,4,True,1,0.0,0)
best2,summ2=summarize(dfpack)
print(summ2)
fig3 = profit_histogram(dfpack[dfpack['Inv_Combo']==best2])
plt.show()

dfmulti = multiperiod(n,100,180,.45,6.5,9.0,2.68,4.21,4,True,6,0.0,.1)
best3,summ3=summarize(dfmulti)
print(summ3)
fig4 = profit_histogram(dfmulti[dfmulti['Inv_Combo']==best3])
plt.show()

