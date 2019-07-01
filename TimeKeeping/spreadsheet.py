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

from datetime import datetime
from pytz import all_timezones

import re
import matplotlib.pyplot as plt
import itertools



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
data.drop(data.index[0], inplace=True)

 
#data.to_csv('sheet_tasks.csv')

#####################################
# Load data entries from calendar
#cal = pd.read_csv("GoogleCalendarExport 2017-10-30 to 2017-11-05.csv", delimiter='\t')
cal = pd.read_csv("GoogleCalendarExport 2017-09-07 to 2018-01-13.csv", delimiter='\t')

# Remove any columns that don't have a key between ()
cal['categorized'] = cal['title'].str.contains("\(")
cal = cal[cal['categorized'] == True]
cal = cal.reset_index()


# Separate the event title and extract the key from the name
key = []
for k in range(len(cal)):
    key.append(re.search('(\()(.\d*)(\))', cal.title[k]).group(2))
    
cal['key'] = key

# Create a new column to signify if the event was a meeting
cal['is_meeting'] = cal['title'].str.contains("\*")

# Rename date columns
cal.rename(columns = {'start': 'start_date', 'end': 'end_date'}, inplace = True)

# Convert date columns
cal['start_date_utc'] = pd.to_datetime(cal['start_date'])
cal['start_date_pt'] = cal['start_date_utc'].dt.tz_localize('US/Pacific')

cal['end_date_utc'] = pd.to_datetime(cal['end_date'])
cal['end_date_pt'] = cal['end_date_utc'].dt.tz_localize('US/Pacific')

# Task time column 
cal['task_time_minutes'] = (cal['end_date_utc'] - cal['start_date_utc']).dt.total_seconds()/60.0

# Select a subset of relevant columns
cal_abr = cal[['key', 'start_date_pt', 'end_date_pt', 'task_time_minutes', 'description', 'is_meeting']]


############### Combine Data ###################
# Combine the time durations/frequency (cal) with the details of each task (data)
df = pd.merge(cal_abr, data, how = 'inner',  left_on = 'key', right_on = 'Task Reference #',)

# Day of Week
df['day_of_week'] = df.start_date_pt.dt.dayofweek
# Year and Week Number
df['year_week'] = df.start_date_pt.dt.strftime('%Y-%U')
         


################ Data Calculations ####################
# Generalize Column Names
date_agg_column = 'year_week'
time_column = 'task_time_minutes'  # Needs to be in minutes
category_column = 'Area'


# Total hours worked
hrs = df.groupby(date_agg_column)[time_column].sum()/60
hrs_df = pd.DataFrame(hrs).reset_index()
hrs_df.rename(columns = {time_column: 'total_hours'}, inplace = True)


# Total time spent per selected category
category = (df.groupby([date_agg_column,category_column])[time_column].sum()/60).reset_index()
category_df = pd.DataFrame(category)
category_df.rename(columns = {time_column: 'category_hours',
                          category_column: 'category'}, inplace = True)

# Make sure every date appears for every category (cross join) - for plotting
category_list = list(df[category_column].unique())
year_week_list = list(df[date_agg_column].unique())
d_cross = pd.DataFrame(list(itertools.product(category_list, year_week_list))) 
d_cross.columns = ['category', date_agg_column]   
    
    
# Combine the two dataframes
d1 = pd.merge(d_cross, hrs_df, how = 'left', left_on = date_agg_column, right_on = date_agg_column)
d2 = pd.merge(d1, category_df, how = 'left', left_on = ['category',date_agg_column], right_on = ['category',date_agg_column])

# Replace all nan values with 0
d2['category_hours'] = d2['category_hours'].fillna(0)

# Percentage of time spent using the category
d2['percentage'] = d2['category_hours']/d2['total_hours']


# Order values by date (for chart below)
d2.sort_values(date_agg_column)

# Create a cumlative sum column for each category
d2['cumsum'] = d2.groupby(['category'])['category_hours'].apply(lambda x: x.cumsum())


# ~~~~~~~~~~~~~~~~~~~~~ Weekly PLOT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Visually display the data
#category_list = ['Python', 'Redshift']
plt.figure(figsize=(8,6))
column_name = 'category_hours'
plt.plot(d2[d2['category']==category_list[0]][date_agg_column], d2[d2['category']==category_list[0]][column_name])
plt.plot(d2[d2['category']==category_list[1]][date_agg_column], d2[d2['category']==category_list[1]][column_name])
#plt.ylim(0,1)
plt.xticks(rotation=45)
#plt.savefig('category_usage.png',  bbox_inches="tight")
plt.show()



# ~~~~~~~~~~~~~~~~~~~~~ CumSum PLOT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Plot the cumulative time spent per each category
objects = year_week_list
pos = np.arange(len(year_week_list))
column_name = 'cumsum'

plt.figure(figsize=(8,6))

for i in range(len(category_list)):
    plt.plot(pos, d2[d2['category']==category_list[i]][column_name])

plt.xticks(pos, objects)
plt.xticks(rotation=45)
plt.legend(category_list, bbox_to_anchor=(1.2,0.5), loc="center")

plt.ylabel('Hours')
plt.xlabel('Year-Week#')
plt.title('Total Time Spent Per ' + category_column)
plt.show()















# Total hours worked, excluding breaks
df[df['Area'] != 'Break'].groupby('year_week')[time_column].sum()/60


df.groupby('Tool/Format')[time_column].sum()/60  

# Total time spent per Skill
df.groupby('Skill')[time_column].sum()/60 



# How much time did I spend before 9am or after 5pm

# Split out by project
df.groupby(['Tool/Format', 'Task'])[time_column].sum()/60 



# Create dataframe of hours working per week (excluding breaks)
df_year_week = df[df['Area'] != 'Break'].groupby('year_week').agg(
                {time_column : [np.sum],
                 'start_date_pt': [np.min]
                }).reset_index()
df_year_week.columns = [''.join(col).strip() for col in df_year_week.columns.values]
df_year_week['week_start'] = df_year_week['start_date_ptamin'].dt.date
df_year_week['task_hours'] = df_year_week['task_time_minutessum']/60


