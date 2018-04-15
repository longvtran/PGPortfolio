#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 03:03:56 2018

@author: longtran
"""

"""
This program cleans the raw gdax data, fill in missing timestamps, creates a 
pandas.Panel of closing prices, and saves it as a pickle file in the database 
folder.

Note: the program assumes that the gdax raw data is saved in a folder called 
"cs341-data".
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime

project_dir = os.path.dirname(__file__)
gdax_dir = os.path.join(project_dir, 'cs341-data/gdax')

def fill_timestamps(pkl_name):
    """
    :param pkl_name: name of the pkl file with pricing data
    Return:
        A dataframe of pricing data, where missing timestamps are filled with
        the most recently available prices.
    """
    gdax = os.path.join(gdax_dir, pkl_name)
    data = pd.read_pickle(gdax)

    # Sort by column 'time'
    data = data.sort_values(by='time')

    # Convert time to seconds
    data['time'] = pd.to_datetime(data['time'], unit='s')
    
    # remove duplicates
    data = data.drop_duplicates(['time'])

    # The common time span of BTC, LTC, and ETH is:
    # from 2016-08-17 04:24:00 to 2018-04-03 21:22:00
    data = data[(data['time'] >= '2016-08-17 04:24:00') & (data['time'] <= '2018-04-03 21:22:00')]
    # Fill missing timestamps with most recently available 
    data.index = pd.DatetimeIndex(data['time'])
    idx_data = pd.date_range(start='2016-08-17 04:24:00', end='2018-04-03 21:22:00', freq='Min')
    data = data.reindex(idx_data, method='pad')
    
    return data


if __name__ == '__main__':
    # Fill missing timestamps in the three datasets
    btc = fill_timestamps('BTC-USD-60.pkl')
    eth = fill_timestamps('ETH-USD-60.pkl')
    ltc = fill_timestamps('LTC-USD-60.pkl')
    
    # Get only the closing prices
    btc_close = btc[['time', 'close']]
    eth_close = eth[['time', 'close']]
    ltc_close = ltc[['time', 'close']]
    
    # Convert the data to a panel
    panel = pd.Panel(items=('close',), major_axis=['BTC', 'ETH', 'LTC'], minor_axis=btc_close.index, dtype=np.float32)
    panel.loc['close', 'BTC', btc_close.index] = btc_close['close'].squeeze()
    panel.loc['close', 'ETH', eth_close.index] = eth_close['close'].squeeze()
    panel.loc['close', 'LTC', ltc_close.index] = ltc_close['close'].squeeze()
    
    #print(ltc_close)
    #print(panel.loc['close', 'BTC'])
    #print(btc_close)
    panel.to_pickle('database/gdax_panel.pkl')