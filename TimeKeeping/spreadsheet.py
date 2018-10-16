# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 13:53:44 2018

@author: Leonova
"""

import os
import pandas as pd
import numpy as np

import gspread
from oauth2client.service_account import ServiceAccountCredentials


# Change the path where additional files are stores
mason_jar_path = 'C:/Users/Leonova/Dropbox/Time Keeping - Mason Jar/'
os.chdir(mason_jar_path)

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
# Load data entries from calendar
cal = pd.read_csv("GoogleCalendarExport 2017-10-30 to 2017-11-05.csv", delimiter='\t')

####################################

# Separate the event title and extract the key from the name
cal['title_part1'], cal['title_part2'] = cal.title.str.split('(').str
cal['key'], cal['title_part2'] = cal.title_part2.str.split(')').str

# Create a new column to signify if the event was a meeting
cal['is_meeting'] = cal['title'].str.contains("\*")


