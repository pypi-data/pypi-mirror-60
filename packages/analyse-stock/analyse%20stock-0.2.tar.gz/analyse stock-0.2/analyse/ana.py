# -*- coding: utf-8 -*-
'''
  To  analyse stock ,basic information
'''
import os
import numpy as np
import pandas as pd
import datetime
from jqdatasdk import *
acc_jq = os.environ["acc_jq"]
passwd_jq = os.environ["passwd_jq"]

auth(acc_jq,passwd_jq)

def get_info(code,type):
    '''
    get basic info : market_cap,net_profit
    code company symbol in stock market
    type = year or quarter
    the order can't changed:report_date,total_assets,total_owners_equities,
    operating_revenue,net_profit,np_parent_company_owners,
    total_assets_parent,total_owners_equities_parent,
    operating_revenue_parent,net_profit_parent,np_parent_company_owners_parent,
    '''
    query_industry = query(finance.STK_COMPANY_INFO.industry_id).filter(finance.STK_COMPANY_INFO.code==code)
    industry = finance.run_query(query_industry).iloc[0,0]
    financeIndustry = ["J66","J67","J68","J69"]
    # fiance and other company has different type table
    if ( industry in  financeIndustry ) :
        query_balance = query(finance.FINANCE_BALANCE_SHEET.report_date,
                            finance.FINANCE_BALANCE_SHEET.total_assets,
                            finance.FINANCE_BALANCE_SHEET.total_owner_equities
                            ).filter(
                            finance.FINANCE_BALANCE_SHEET.code == code,
                            finance.FINANCE_BALANCE_SHEET.report_type== 0)
        df_balance = finance.run_query(query_balance)
        query_income = query(finance.FINANCE_INCOME_STATEMENT.report_date,
                   finance.FINANCE_INCOME_STATEMENT.operating_revenue,
                   finance.FINANCE_INCOME_STATEMENT.net_profit,
                   finance.FINANCE_INCOME_STATEMENT.np_parent_company_owners
                   ).filter(finance.FINANCE_INCOME_STATEMENT.code == code,
                   finance.FINANCE_INCOME_STATEMENT.report_type==0)
        df_income = finance.run_query(query_income)
        query_balance_parent = query(finance.FINANCE_BALANCE_SHEET_PARENT.report_date,
                            finance.FINANCE_BALANCE_SHEET_PARENT.total_assets,
                            finance.FINANCE_BALANCE_SHEET_PARENT.total_owner_equities
                            ).filter(
                            finance.FINANCE_BALANCE_SHEET_PARENT.code == code,
                            finance.FINANCE_BALANCE_SHEET_PARENT.report_type== 0)
        df_balance_parent = finance.run_query(query_balance_parent)
        query_income_parent = query(finance.FINANCE_INCOME_STATEMENT_PARENT.report_date,
                   finance.FINANCE_INCOME_STATEMENT_PARENT.operating_revenue,
                   finance.FINANCE_INCOME_STATEMENT_PARENT.net_profit,
                   finance.FINANCE_INCOME_STATEMENT_PARENT.np_parent_company_owners
                   ).filter(finance.FINANCE_INCOME_STATEMENT_PARENT.code == code,
                   finance.FINANCE_INCOME_STATEMENT_PARENT.report_type==0)
        df_income_parent = finance.run_query(query_income)
        df = df_balance.join(df_income.set_index('report_date'),on='report_date',how='outer')
        df_parent = df_balance_parent.join(df_income_parent.set_index('report_date'),on='report_date',how='outer')
        df_parent.rename(columns={'total_assets':'total_assets_parent',
                                  'total_owner_equities':'total_owner_equities_parent',
                                  'operating_revenue':'operating_revenue_parent',
                                  'net_profit':'net_profit_parent',
                                  'np_parent_company_owners':'np_parent_company_owners_parent',
                                  },inplace=True)
    else :
        query_balance = query(finance.STK_BALANCE_SHEET.report_date,
                            finance.STK_BALANCE_SHEET.total_assets,
                            finance.STK_BALANCE_SHEET.total_owner_equities
                            ).filter(
                            finance.STK_BALANCE_SHEET.code == code,
                            finance.STK_BALANCE_SHEET.report_type== 0)
        df_balance = finance.run_query(query_balance)
        query_income = query(finance.STK_INCOME_STATEMENT.report_date,
                   finance.STK_INCOME_STATEMENT.total_operating_revenue,
                   finance.STK_INCOME_STATEMENT.net_profit,
                   finance.STK_INCOME_STATEMENT.np_parent_company_owners
                   ).filter(finance.STK_INCOME_STATEMENT.code == code,
                   finance.STK_INCOME_STATEMENT.report_type==0)
        df_income = finance.run_query(query_income)
        query_balance_parent = query(finance.STK_BALANCE_SHEET_PARENT.report_date,
                            finance.STK_BALANCE_SHEET_PARENT.total_assets,
                            finance.STK_BALANCE_SHEET_PARENT.total_owner_equities
                            ).filter(
                            finance.STK_BALANCE_SHEET_PARENT.code == code,
                            finance.STK_BALANCE_SHEET_PARENT.report_type== 0)
        df_balance_parent = finance.run_query(query_balance_parent)
        query_income_parent = query(finance.STK_INCOME_STATEMENT_PARENT.report_date,
                   finance.STK_INCOME_STATEMENT_PARENT.total_operating_revenue,
                   finance.STK_INCOME_STATEMENT_PARENT.net_profit,
                   finance.STK_INCOME_STATEMENT_PARENT.np_parent_company_owners
                   ).filter(finance.STK_INCOME_STATEMENT_PARENT.code == code,
                   finance.STK_INCOME_STATEMENT_PARENT.report_type==0)
        df_income_parent = finance.run_query(query_income_parent)
        df = df_balance.join(df_income.set_index('report_date'),on='report_date',how='outer')
        df_parent = df_balance_parent.join(df_income_parent.set_index('report_date'),on='report_date',how='outer')
        df_parent.rename(columns={'total_assets':'total_assets_parent',
                                  'total_owner_equities':'total_owner_equities_parent',
                                  'total_operating_revenue':'total_operating_revenue_parent',
                                  'net_profit':'net_profit_parent',
                                  'np_parent_company_owners':'np_parent_company_owners_parent',
                                  },inplace=True)
    df = df.join(df_parent.set_index('report_date'),on='report_date',how='outer')
    df = df.sort_values(by='report_date')
    df.reset_index(drop=True, inplace=True)
    all_cap = []
    query_market_cap = query(valuation.market_cap).filter(valuation.code == code) 
    for idate in df['report_date']:
        cap = get_fundamentals(query_market_cap,date=idate)['market_cap']
        if cap.empty:
            all_cap.append(np.nan)
        else:
            all_cap.append(cap[0])
    df['market_cap'] = all_cap
    if type == "year" :
        df = df[df['report_date'].astype(str).str.contains('12-31')]
#    else :
#        row_num = df.shape[0]
#        col_num = df.shape[1]
#        for row_id in range(row_num):
#            if df.iloc[row_id,0][5:]  == '03-31':
#                pass
#            elif  df.iloc[row_id,0][5:]  == '06-30':
#                if row_id == 0:
#                    df.iloc[row_id,3:5] = df.iloc[row_id,]/2
#                    df.iloc[row_id,3] = df.iloc[row_id,]/2
#                    df.iloc[row_id,3] = df.iloc[row_id,]/2
#                    df.iloc[row_id,3] = df.iloc[row_id,]/2
#                    df[''][row_id] = df[''][row_id]/2
#                else:
#
#            elif  df.iloc[row_id,0][5:]  == '09-30':
#            elif  df.iloc[row_id,0][5:]  == '12-31':
    dlen = len(df)
    df.reset_index(drop=True,inplace=True)
    df.index = df['report_date']
    return df 


def get_growth(code):
    data = get_info(code,"year")    
    df2.rename(columns={'total_operating_revenue':'total_operating_revenue_parent', 
               'net_profit':'net_profit_parent',
               'np_parent_company_owners':'np_parent_company_owners_parent'}, inplace = True)
    df = df1.join(df2.set_index('report_date'),on='report_date',how='outer')
    back = df 
    df = pd.concat([df.iloc[:,0],df.iloc[:,1:].pct_change(fill_method=None)],axis=1)
    colnum = len(df.columns)
    rownum = len(df)
    for colid in range(1,colnum):
        for rowid in range(rownum):
            if not(pd.isna(df.iloc[rowid,colid])):
                df.iloc[rowid,colid] = str(round(df.iloc[rowid,colid]*100,0)) + "%"
    return  {"primitive":back,"growth":df}

