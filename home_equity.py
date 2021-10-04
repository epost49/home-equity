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
import pdb


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
    

def calc_d_savings(d_incomes, d_expenses):
    #d_savings = d_inc - d_inc_tax - d_mortgage_pmt - d_hoa - d_prop_tax - d_repairs
    #d_savings = 0
    #for key in incomes:
    #    d_savings += incomes[key]
    #for key in expenses:
    #    d_savings -= expenses[key]
    
    d_savings = np.sum(np.transpose(d_incomes), axis=0) - np.sum(np.transpose(d_expenses), axis=0)
    return d_savings

'''
def calc_d_wealth(d_home_val, d_savings, d_princ_pmt):
    d_wealth = d_home_val + d_savings + d_princ_pmt
    return d_wealth
'''

def calc_d_wealth(d_assets, d_liabilities):
    # This calculates a single delta wealth or an array of delta wealths
    #d_wealth = np.sum(d_assets) - np.sum(d_liabilities)
    d_wealth =  np.sum(np.transpose(d_assets), axis=0) - np.sum(np.transpose(d_liabilities), axis=0)
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
  

def simple_job_arr(initial_salary=0, annual_raise=0, num_periods=60):
    job_arr = []
    for i in range(num_periods):
        raise_period = np.floor(i / 12)
        current_salary = initial_salary * (1 + annual_raise) ** raise_period
        monthly_salary = current_salary / 12
        job_arr.append(monthly_salary)
    
    return np.array(job_arr)



def buy_home_df(income_arr, home_price=600000, down_pmt_pct=0.2, 
                 int_rate=0.025, mortgage_yrs=15, initial_total_income=125000, 
                 annual_raise_rate=0.03, monthly_hoa=400, 
                 prop_tax_rate=0.0125, house_apprecation_rate=0.03, 
                 stock_appreciation_rate=0.03, home_repair_rate=0.01, 
                 initial_home_asset=0, initial_home_debt=0, initial_savings=150000):
    annual_prop_tax = home_price * prop_tax_rate  # need to verify tax rate
    annual_repairs = home_price * home_repair_rate  # assume constant % of home value for repairs
    d_home_val = home_price * house_apprecation_rate / 12  # assume 3% annual appreciation
    num_periods = 12 * mortgage_yrs
    loan_month_arr = np.arange(num_periods)
    hoa_arr = np.repeat(monthly_hoa, num_periods)  # monthly HOA fees
    #period_arr = np.arange(num_periods) + 1  # array of months, starting at 1
    down_pmt = down_pmt_pct * home_price
    loan_amt = home_price - down_pmt
    monthly_pmt = -npf.pmt(int_rate / 12, num_periods, loan_amt)
    monthly_prin_pmts = npf.ppmt(int_rate / 12, 
                                np.arange(mortgage_yrs * 12) + 1, 
                                mortgage_yrs  *12, 
                                -loan_amt)
    monthly_int_pmts = npf.ipmt(int_rate / 12, 
                                np.arange(mortgage_yrs * 12) + 1, 
                                mortgage_yrs  *12, 
                                -loan_amt)
    
    # make job income functions
    #job1_inc = make_job_arr(salary=123000, num_periods=num_periods)
    #job2_inc = make_job_arr(salary=60000, num_periods=num_periods)
    #inc_arr = job1_inc + job2_inc
    
    # Initialize monthly data arrays to capture home purchase in 1st 2 months
    month_arr = np.array([0, 1])
    d_income_arr = np.repeat(income_arr[0], 2)
    d_inc_tax_arr = np.repeat(calc_d_inc_tax(income_arr[0], 0), 2)
    d_prop_tax_arr = np.array([0, 0])
    d_home_asset_arr = np.array([0, home_price])
    d_debt_arr = np.array([0, loan_amt])
    d_int_pmt_arr = np.array([0, 0])
    d_prin_pmt_arr = np.array([0, 0])
    d_hoa_arr = np.array([0, 0])
    d_repairs_arr = np.array([0, 0])
    d_down_pmt_arr = np.array([0, down_pmt])
    #pdb.set_trace()
    d_expenses = [d_inc_tax_arr, d_prop_tax_arr, d_int_pmt_arr, 
                  d_prin_pmt_arr, d_hoa_arr, d_repairs_arr, d_down_pmt_arr]
    d_savings_arr = d_income_arr - np.sum(d_expenses,axis=0)
    d_wealth_arr = d_savings_arr + d_home_asset_arr - d_debt_arr
    
    #d_savings_arr = calc_d_savings(d_income_arr, d_expenses)
    #d_wealth_arr = calc_d_wealth(d_savings_arr + d_home_asset_arr, d_debt_arr)
    #np.array([calc_d_wealth(), calc_d_wealth()])  # derived

    # loop over each month and fill in arrays with monthly deltas
    cur_month = month_arr[-1]  # current month will increment from end of month_arr
    for n in loan_month_arr:
        cur_month += 1
        #d_inc1 = job1_inc[n]
        #d_inc2 = job2_inc[n]
        d_inc = income_arr[n]
        d_int_pmt = monthly_int_pmts[n]
        d_mortgage_pmt = monthly_pmt
        d_prin_pmt = monthly_prin_pmts[n]
        d_prop_tax = annual_prop_tax / 12
        d_hoa = hoa_arr[n]
        d_repairs = annual_repairs / 12
        d_inc_tax = calc_d_inc_tax(d_inc, d_int_pmt)
        #incomes = {'job1_income':d_inc1,
        #           'job2_income':d_inc2}
        #expenses = {'mortgage_pmt':d_mortgage_pmt,
        #            'HOA':d_hoa,
        #            'PropTax':d_prop_tax,
        #            'IncomeTax':d_inc_tax,
        #            'Repairs':d_repairs}
        d_expenses = [d_mortgage_pmt, d_hoa, d_prop_tax, d_inc_tax, d_repairs]
        d_savings = calc_d_savings(d_inc, d_expenses)
        #d_wealth = calc_d_wealth(d_home_val, d_savings, d_princ_pmt)
        d_asset_arr = [d_home_val, d_savings]
        d_liability_arr = [-d_prin_pmt]
        d_wealth = calc_d_wealth(d_asset_arr, d_liability_arr)
        #pdb.set_trace()
        # Append monthly data to arrays
        month_arr = np.append(month_arr, cur_month)
        d_income_arr = np.append(d_income_arr, d_inc)
        d_inc_tax_arr = np.append(d_inc_tax_arr, d_inc_tax)
        d_prop_tax_arr = np.append(d_prop_tax_arr, d_prop_tax)
        d_home_asset_arr = np.append(d_home_asset_arr, d_home_val)
        d_debt_arr = np.append(d_debt_arr, -d_prin_pmt)
        d_int_pmt_arr = np.append(d_int_pmt_arr, d_int_pmt)
        d_prin_pmt_arr = np.append(d_prin_pmt_arr, d_prin_pmt)
        d_hoa_arr = np.append(d_hoa_arr, d_hoa)
        d_repairs_arr = np.append(d_repairs_arr, d_repairs)
        d_savings_arr = np.append(d_savings_arr, d_savings)
        d_wealth_arr = np.append(d_wealth_arr, d_wealth)
    
    #pdb.set_trace()
    HomeAsset = initial_home_asset + np.cumsum(d_home_asset_arr)
    HomeDebt = initial_home_debt + np.cumsum(d_debt_arr)
    HomeEquity = HomeAsset - HomeDebt
    PctLoanPaid = 100 * (1 - HomeDebt / loan_amt)
    Savings = initial_savings + np.cumsum(d_savings_arr)
    Wealth = initial_home_asset - initial_home_debt + initial_savings + np.cumsum(d_wealth_arr)
    #pdb.set_trace()
    data = {'Month': month_arr,
            'd_Income': d_income_arr,
            'd_IncomeTax': d_inc_tax_arr,
            'd_HomeAsset': d_home_asset_arr,
            'd_Debt': d_debt_arr,
            'd_PropertyTax': d_prop_tax_arr,
            'd_PrinciplePmt': d_prin_pmt_arr,
            'd_InterestPmt': d_int_pmt_arr,
            'd_HOA': d_hoa_arr,
            'd_Repairs': d_repairs_arr,
            'd_Savings': d_savings_arr,
            'd_Wealth': d_wealth_arr,
            'HomeAsset': HomeAsset, 
            'HomeDebt': HomeDebt,
            'HomeEquity': HomeEquity,
            'PctLoanPaid': PctLoanPaid,
            'Savings': Savings,
            'Wealth': Wealth}
    df = pd.DataFrame.from_dict(data).set_index('Month')
    return df
    
    

if __name__ == "__main__":
    income=simple_job_arr(initial_salary=125000, annual_raise=0.03, num_periods=180)
    df = buy_home_df(income, int_rate=0.026)
    
    '''
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
    '''