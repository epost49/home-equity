#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  7 17:22:29 2021

@author: ethan
"""

import numpy as np
import matplotlib.pyplot as plt
import numpy_financial as npf
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


def mortgage_summary(home_price, int_rate, mortgage_yrs, down_pmt):
    num_periods = 12 * mortgage_yrs
    #period_arr = np.arange(num_periods) + 1  # array of months, starting at 1
    loan_amt = home_price - down_pmt
    #int_pmts = -npf.ipmt(int_rate / 12, period_arr, num_periods, loan_amt)  # array of monthly payments towards interest
    #prin_pmts = -npf.ppmt(int_rate / 12, period_arr, num_periods, loan_amt)  # array of montly payments towards principle
    monthly_pmt = -npf.pmt(int_rate / 12, num_periods, loan_amt)
    total_int = monthly_pmt * num_periods - loan_amt
    indent = "    "
    print("Mortgage Summary")
    print(indent + "Home price: $" + '{:.2f}'.format(home_price))
    print(indent + "Down payment: $" + '{:.2f}'.format(down_pmt) + 
            " (" + '{:.0f}'.format(down_pmt / home_price * 100) + "%)")
    print(indent + "Loan amount: $" + '{:.2f}'.format(loan_amt))
    print(indent + "Interest rate: " + '{:.2f}'.format(int_rate * 100) + "%")
    print(indent + "Mortgage years: " + '{:.0f}'.format(mortgage_yrs))
    print(indent + "Monthy payment: $" + '{:.2f}'.format(monthly_pmt))
    print(indent + "Total interest payable: $" + '{:.2f}'.format(total_int))
    print(indent + "Interest to loan ratio: " + '{:.2f}'.format(total_int / loan_amt))    
    

def calc_d_savings(incomes, expenses):
    #d_savings = d_inc - d_inc_tax - d_mortgage_pmt - d_hoa - d_prop_tax - d_repairs
    d_savings = 0
    for key in incomes:
        d_savings += incomes[key]
    for key in expenses:
        d_savings -= expenses[key]
    return d_savings


def calc_d_wealth(d_home_val, d_savings, d_princ_pmt):
    d_wealth = d_home_val + d_savings + d_princ_pmt
    return d_wealth


def calc_d_inc_tax(d_inc, d_int_pmt, annual_periods=12):
    taxes = PayrollTax(annual_periods * d_inc, annual_periods * d_int_pmt)  # estimate tax based on annualized income
    d_inc_tax = (taxes['FederalTax'] + taxes['StateTax'] + taxes['FICA']) / annual_periods  # convert back (e.g. to monthly)
    return d_inc_tax
    

def PayrollTax(BaseSalary, Adjustments):
    AGI = BaseSalary - Adjustments
    FederalTaxBrackets = [(.1, 9875)
                        , (.12, 40125)
                        , (.22, 85525)
                        , (.24, 163300)
                        , (.32, 207340)
                        , (.35, 311025)
                        , (.37, 11311025)]

    # Filing jointly
    # FederalTaxBrackets = [(.1, 19750)
    #                      , (.12, 80250)
    #                      , (.22, 171050)
    #                      , (.24, 326600)
    #                      , (.32, 414700)
    #                      , (.35, 622050)
    #                      , (.37, 11311025)]
    FederalTax = 0
    last_bracket = 0
    for percent, bracket in FederalTaxBrackets:
        if bracket < AGI:
            FederalTax = FederalTax + (bracket - last_bracket) * percent
        else:
            FederalTax = FederalTax + (AGI - last_bracket) * percent
            break
        last_bracket = bracket

    StateTax = AGI * 0.09
    FICA = AGI * .0765  # SS + Medicare
    #Other = AGI * .1

    return {'StateTax': StateTax
        , 'FICA': FICA
        , 'FederalTax': FederalTax}
  

def make_job_arr(salary=0, annual_raise=0, num_periods=60):
    job_arr = []
    for i in range(num_periods):
        raise_factor = np.floor(i / 12)
        current_salary = salary * (1 + annual_raise) ** raise_factor
        monthly_salary = current_salary / 12
        job_arr.append(monthly_salary)
    
    return job_arr



def calc_wealth_arr(home_price, down_pmt, int_rate, mortgage_yrs, annual_income):
    annual_prop_tax = home_price * 0.0125  # need to verify tax rate
    annual_repairs = home_price * 0.01  # assume 1% of home value for repairs
    d_home_val = home_price * 0.03 / 12  # assume 3% annual appreciation
    d_hoa = 300  # monthly HOA fee
    num_periods = 12 * mortgage_yrs
    #period_arr = np.arange(num_periods) + 1  # array of months, starting at 1
    loan_amt = home_price - down_pmt
    monthly_pmt = -npf.pmt(int_rate / 12, num_periods, loan_amt)
    monthly_princ_pmts = npf.ppmt(int_rate / 12, 
                                np.arange(mortgage_yrs * 12) + 1, 
                                mortgage_yrs  *12, 
                                -loan_amt)
    monthly_int_pmts = npf.ipmt(int_rate / 12, 
                                np.arange(mortgage_yrs * 12) + 1, 
                                mortgage_yrs  *12, 
                                -loan_amt)
    
    # make job income functions
    job1_inc = make_job_arr(salary=123000)
    job2_inc = make_job_arr(salary=60000)
    
    # loop over each month and fill in arrays with monthly deltas
    wealth_arr = []
    for n in range(num_periods):
        d_inc1 = job1_inc[n]
        d_inc2 = job2_inc[n]
        d_inc = d_inc1 + d_inc2
        d_int_pmt = monthly_int_pmts[n]
        d_mortgage_pmt = monthly_pmt[n]
        d_princ_pmt = monthly_princ_pmts[n]
        d_prop_tax = annual_prop_tax / 12
        d_repairs = annual_repairs / 12
        d_inc_tax = calc_d_inc_tax(d_inc, d_int_pmt)
        incomes = {'job1_income':d_inc1,
                   'job2_income':d_inc2}
        expenses = {'mortgage_pmt':d_mortgage_pmt,
                    'HOA':d_hoa,
                    'PropTax':d_prop_tax,
                    'IncomeTax':d_inc_tax,
                    'Repairs':d_repairs}
        d_savings = calc_d_savings(incomes, expenses)
        d_wealth = calc_d_wealth(d_home_val, d_savings, d_princ_pmt)
        wealth_arr.append(d_wealth)
    
    return wealth_arr
    
    

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