#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  7 17:22:29 2021

@author: ethan
"""

import numpy as np
import matplotlib.pyplot as plt
# import numpy-financial as npf
import pandas as pd
import seaborn as sb


def payment_schedule(home_price, initial_savings, down_payment, interest_rate, loan_years, rent, monthly_budget):
    num_periods = loan_years * 12
    home_value = np.repeat(home_price, num_periods) # array of home value over time (unvarying)
    loan_amt = home_price - down_payment
    period_arr = np.linspace(1, num_periods, num=num_periods)  # array of payment periods
    if home_price == 0:
        int_pmt = np.repeat(0, num_periods)
        prin_pmt = np.repeat(0, num_periods)
    else:
        int_pmt = -np.ipmt(interest_rate / 12, period_arr, num_periods, loan_amt)  # array of monthly payments towards interest
        prin_pmt = -np.ppmt(interest_rate / 12, period_arr, num_periods, loan_amt)  # array of montly payments towards principle
    
    tot_int_paid = np.cumsum(int_pmt)  # array of cumulative interest paid
    tot_prin_paid = np.cumsum(prin_pmt)  # array of cumulative principle paid
    tot_rent = np.cumsum(np.repeat(rent, num_periods))  # array of cumulative rent paid
    debt = loan_amt - tot_prin_paid  # array of total debt remaining
    equity = home_value - debt
    monthly_savings = monthly_budget - int_pmt - prin_pmt - rent  # array of monthly budget not put towards mortgage payment or rent
    monthly_savings[0] = monthly_savings[0] + initial_savings - down_payment  # monthly savings starts with initial savings less down payment
    tot_savings = np.cumsum(monthly_savings)  # array of cumulative monthly savings
    wealth = equity + tot_savings  # array of total wealth
    df = pd.DataFrame(data={'Period':period_arr, 
                            'Interest Pmt':int_pmt, 
                            'Principle Pmt':prin_pmt, 
                            'Total Interest Paid':tot_int_paid, 
                            'Total Principle Paid':tot_prin_paid,
                            'Total Rent Paid':tot_rent,
                            'Equity':equity,
                            'Debt':np.round(debt, decimals=2),
                            'Monthly Savings':monthly_savings,
                            'Total Savings':tot_savings,
                            'Wealth':wealth
                           })
    return df


def equity_plotter(df, y_cols):
    # line plot of debt, equity, wealth vs period (time)
    df_melt = df.melt(id_vars=['Period'], 
                           value_vars=y_cols, 
                           var_name='Variable', 
                           value_name='Dollars ($)')
    sb.lineplot(data=df_melt,x='Period',y='Dollars ($)',hue='Variable')
    
    
def compare_scenarios(df_own, df_rent):
    #df_own['Rent/Own'] = np.repeat('Own',df_own.shape[0])
    #df_rent['Rent/Own'] = np.repeat('Rent',df_rent.shape[0])
    y_cols = ['Debt', 'Equity', 'Wealth']
    df_own_melt = df_own.melt(id_vars=['Period'], 
                           value_vars=y_cols, 
                           var_name='Variable', 
                           value_name='Dollars ($)')
    df_own_melt['Rent/Own'] = np.repeat('Own',df_own_melt.shape[0])
    df_rent_melt = df_rent.melt(id_vars=['Period'], 
                           value_vars=y_cols, 
                           var_name='Variable', 
                           value_name='Dollars ($)')
    df_rent_melt['Rent/Own'] = np.repeat('Rent',df_rent_melt.shape[0])
    df_combined = pd.concat([df_own_melt, df_rent_melt],ignore_index=True)
    sb.relplot(data=df_combined, x='Period',y='Dollars ($)',hue='Variable', kind="line", col='Rent/Own')
    return df_combined


if __name__ == "__main__":
    home_price = 500000
    down_payment = 100000
    initial_savings = 2*down_payment
    interest_rate = 0.09
    term_years = 30
    rent = 1000
    monthly_budget = 3500
    df_own = payment_schedule(home_price,
                              initial_savings,
                              down_payment,
                              interest_rate,
                              term_years,
                              0,
                              monthly_budget
                              )
    df_rent = payment_schedule(0,
                               initial_savings,
                               0,
                               0,
                               term_years,
                               rent,
                               monthly_budget
                               )  # this is a bit messy
    df = payment_schedule(home_price,
                          initial_savings,
                          down_payment,
                          interest_rate,
                          term_years,
                          rent,
                          monthly_budget
                          )
    y_cols = ['Debt', 'Equity', 'Wealth']
    equity_plotter(df, y_cols)
    compare_scenarios(df_own, df_rent)