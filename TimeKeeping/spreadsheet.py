# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 13:53:44 2018

@author: Leonova
"""

import pandas as pd

import gspread
from oauth2client.service_account import ServiceAccountCredentials


scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
gc = gspread.authorize(credentials)


# Open a specific worksheet from a google spreadsheet
#sheet = gc.open("Mason Jar Tasks").sheet1
sheet = gc.open("Mason Jar Tasks").worksheet('List of Tasks (2017)')




data = sheet.get_all_values()
data = pd.DataFrame(data)
data.columns = data.iloc[0]
data.reindex(data.index.drop(0))


#data.to_csv('sheet_tasks.csv')

#####################################




