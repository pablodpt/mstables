import pandas as pd
import numpy as np
import sqlite3
import json
import sys
import re
import os


class DataFrames():

    db_file = 'db/mstables.sqlite' # Standard db file name

    def __init__(self, file = db_file):

        print('Creating intial DataFrames from file {}...'.format(file))

        self.conn = sqlite3.connect(
            file, detect_types=sqlite3.PARSE_COLNAMES)
        self.cur = self.conn.cursor()

        # Row Headers
        colheaders = self.table('ColHeaders', True)
        self.colheaders = colheaders.set_index('id')

        # Dates and time references
        timerefs = self.table('TimeRefs', True)
        self.timerefs = timerefs.set_index('id').replace(['', '—'], None)

        # Reference tables
        self.urls = self.table('URLs', True)
        self.securitytypes = self.table('SecurityTypes', True)
        self.tickers = self.table('Tickers', True)
        self.sectors = self.table('Sectors', True)
        self.industries = self.table('Industries', True)
        self.styles = self.table('StockStyles', True)
        self.exchanges = self.table('Exchanges', True)
        self.countries = (self.table('Countries', True)
            .rename(columns={'a2_iso':'country_c2', 'a3_un':'country_c3'}))
        self.companies = self.table('Companies', True)
        self.currencies = self.table('Currencies', True)
        self.stocktypes = self.table('StockTypes', True)
        #self.fetchedurls = self.table('Fetched_urls', True)

        # Master table
        self.master = self.table('Master', True)

        print('Initial DataFrames created.')


    def quoteheader(self):
        return self.table('MSheader')


    def valuation(self):
        # Create DataFrame
        val = self.table('MSvaluation')

        # Rename column headers with actual year values
        yrs = val.iloc[0, 2:13].replace(self.timerefs['dates']).to_dict()
        cols = val.columns[:13].values.tolist() + list(map(
            lambda col: ''.join([col[:3], yrs[col[3:]]]), val.columns[13:]))
        val.columns = cols

        # Resize and reorder columns
        val = val.set_index(['exchange_id', 'ticker_id']).iloc[:, 11:]

        return val


    def keyratios(self):
        yr_cols = ['Y0', 'Y1', 'Y2', 'Y3', 'Y4', 'Y5', 'Y6',
                    'Y7', 'Y8', 'Y9', 'Y10']
        keyratios = self.table('MSfinancials')
        for yr in yr_cols:
            keyratios = (keyratios
             .merge(self.timerefs, left_on=yr, right_on='id')
             .drop(yr, axis=1).rename(columns={'dates':yr})
            )
        keyratios.loc[:, 'Y0':'Y9'] = (
            keyratios.loc[:, 'Y0':'Y9'].astype('datetime64'))

        return keyratios


    def finhealth(self):
        finanhealth = self.table('MSratio_financial')
        return finanhealth


    def profitability(self):
        profitab = self.table('MSratio_profitability')
        return profitab


    def growth(self):
        growth = self.table('MSratio_growth')
        return growth


    def cfhealth(self):
        cfhealth = self.table('MSratio_cashflow')
        yr_cols = [col for col in cfhealth.columns
                    if col.startswith('cf_Y')]

        for col in yr_cols:
            cfhealth = (cfhealth
             .merge(self.timerefs, left_on=col, right_on='id')
             .drop(col, axis=1).rename(columns={'dates':col})
            )

        return cfhealth


    def efficiency(self):
        efficiency = self.table('MSratio_efficiency')
        return efficiency

    # Income Statement - Annual
    def annualIS(self):
        rep_is_yr = self.table('MSreport_is_yr')

        '''# Replace date Columns
        rep_is_yr.iloc[:,2:8] = (rep_is_yr.iloc[:,2:8]
            .replace(self.timerefs['dates']))

        # Format Date Columns
        rep_is_yr.iloc[:,2:7] = (rep_is_yr.iloc[:,2:7].astype('datetime64'))

        # Replace column header values in label columns
        cols = [col for col in rep_is_yr.columns if 'label' in col]
        rep_is_yr[cols] = (
            rep_is_yr[cols].replace(self.colheaders['header']))'''

        return rep_is_yr

    # Income Statement - Quarterly
    def quarterlyIS(self):
        rep_is_qt = self.table('MSreport_is_qt')

        '''rep_is_qt.iloc[:,2:8] = (rep_is_qt.iloc[:,2:8]
            .replace(self.timerefs['dates']))
        rep_is_qt.iloc[:,2:7] = (rep_is_qt.iloc[:,2:7].astype('datetime64'))
        cols = [col for col in rep_is_qt.columns if 'label' in col]
        rep_is_qt[cols] = (
            rep_is_qt[cols].replace(self.colheaders['header']))'''

        return rep_is_qt

    # Balance Sheet - Annual
    def annualBS(self):
        rep_bs_yr = self.table('MSreport_bs_yr')

        '''rep_bs_yr.iloc[:,2:7] = (rep_bs_yr.iloc[:,2:7]
            .replace(self.timerefs['dates'])
            .astype('datetime64'))
        cols = [col for col in rep_bs_yr.columns if 'label' in col]
        rep_bs_yr[cols] = (
            rep_bs_yr[cols].replace(self.colheaders['header']))'''

        return rep_bs_yr

    # Balance Sheet - Quarterly
    def quarterlyBS(self):
        rep_bs_qt = self.table('MSreport_bs_qt')

        '''rep_bs_qt.iloc[:,2:7] = (rep_bs_qt.iloc[:,2:7]
            .replace(self.timerefs['dates'])
            .astype('datetime64'))
        cols = [col for col in rep_bs_qt.columns if 'label' in col]
        rep_bs_qt[cols] = (
            rep_bs_qt[cols].replace(self.colheaders['header']))'''

        return rep_bs_qt

    # Cashflow Statement - Annual
    def annualCF(self):
        rep_cf_yr = self.table('MSreport_cf_yr')

        '''rep_cf_yr.iloc[:,2:8] = (rep_cf_yr.iloc[:,2:8]
            .replace(self.timerefs['dates']))
        rep_cf_yr.iloc[:,2:7] = (rep_cf_yr.iloc[:,2:7].astype('datetime64'))
        cols = [col for col in rep_cf_yr.columns if 'label' in col]
        rep_cf_yr[cols] = (
            rep_cf_yr[cols].replace(self.colheaders['header']))'''

        return rep_cf_yr

    # Cashflow Statement - Quarterly
    def quarterlyCF(self):
        rep_cf_qt = self.table('MSreport_cf_qt')

        '''rep_cf_qt.iloc[:,2:8] = (rep_cf_qt.iloc[:,2:8]
            .replace(self.timerefs['dates']))
        rep_cf_qt.iloc[:,2:7] = (rep_cf_qt.iloc[:,2:7].astype('datetime64'))
        cols = [col for col in rep_cf_qt.columns if 'label' in col]
        rep_cf_qt[cols] = (
            rep_cf_qt[cols].replace(self.colheaders['header']))'''

        return rep_cf_qt

    # 10yr Price History
    def priceHistory(self):
        return self.table('MSpricehistory')


    def table(self, tbl, prnt = False):
        self.cur.execute('SELECT * FROM {}'.format(tbl))
        cols = list(zip(*self.cur.description))[0]

        try:
            if prnt == True:
                msg = 'Creating DataFrame \'{}\' ...'
                print(msg.format(tbl.lower()))
            return pd.DataFrame(self.cur.fetchall(), columns=cols)
        except:
            raise


    def __del__(self):
        self.cur.close()
        self.conn.close()
