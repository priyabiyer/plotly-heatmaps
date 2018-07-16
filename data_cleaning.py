# Import packages for DASH app
import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc

# Import other necessary packages
import pandas as pd
import numpy as np
from numpy import *
import pymysql
import settings

with open(settings.FILE_PATH, 'r') as f:
    # Reads text file
    data = f.read()
# Split data into substrings
lines = data.split("\n")
# Create empty dictionary
conf = {}
# Split keys and values in text file for input into dictionary
for line in lines:
    try:
        key, val = line.split(":")
        val = val.strip().replace("'", "")
    except ValueError:
        print("Invalid file")
        break
    # Create keys and values in dictionary
    conf[key] = val
conf

# Connect to MySQL database by pulling config info from file into function 
def connect(host, user, password, database):
    connection = {'host': host,
            'user': user,
                  'port': 3306,
            'password': password,
            'db': database}

    conn = pymysql.connect(**connection)
    
    # Query data from database and turn into Pandas dataframe
    df = pd.read_sql_query("SELECT * FROM simulated_head_count INNER JOIN job_level_linear ON job_level_linear.job_level = simulated_head_count.job_level;", conn)
    cur = conn.cursor()
    
    # close connection
    cur.close()
    conn.close()
    return df

# Initialize function above
dataset = connect(conf['host'], conf['user'], conf['password'], conf['database'])

# Remove all duplicate columns that resulted from merging of MySQL tables
dataset1 = dataset.loc[:, ~dataset.columns.duplicated()]

# Function to replace category names in a column 
def rename(dataset, column, Old1, New1, Old2, New2, Old3, New3, Old4, New4, Old5, New5, Old6, New6, Old7, New7):
    return dataset[column].replace({Old1: New1, Old2: New2, Old3: New3, Old4: New4, Old5: New5, Old6: New6, Old7: New7}) 

dataset1['toplevel_manager_org'] = rename(dataset1, 'toplevel_manager_org', 'Pharma Global Technical Operations', 'PT', 'Commercial Operations', 'CMG', 'Corporate Groups', 'Corporate', 'Product Development', 'PD', 'Medical Affairs', 'CMG', 'Global Product Strategy', 'GPS', 'Genentech (Not mapped)', 'Not mapped')


# Function to drop rows that contain column with specific categories 
def drop_row(dataset, column, cat_name):
    return dataset.loc[~dataset[column].str.contains(cat_name)]

dataset1 = drop_row(dataset1, 'toplevel_manager_org', "Latin America Region")
dataset1 = drop_row(dataset1, 'toplevel_manager_org', "Roche Partnering")
dataset1 = drop_row(dataset1, 'toplevel_manager_org', "Not mapped")
dataset1 = drop_row(dataset1, 'hierarchy_label', "N/00")

# Create dataframe with cross-tabulation of # of employees in each sub-group by level
employee_count = pd.crosstab(dataset1.toplevel_manager_org, dataset1.hierarchy_label)

# Function to create dataframe with percentage of X that is Y; In this case % of employees who are managers 
def perc_crosstabs(dataset, column, column1_crosstab, column2_crosstab, variable1, variable2):
    newdataset1 = dataset[dataset[column] == variable1]
    newdataset2 = dataset[dataset[column] == variable2]
    new_crosstabs1 = pd.crosstab(newdataset1[column1_crosstab], newdataset1[column2_crosstab], margins=False)
    new_crosstabs2 = pd.crosstab(newdataset2[column1_crosstab], newdataset2[column2_crosstab], margins=False)
    final = (new_crosstabs1 / (new_crosstabs1 + new_crosstabs2)) * 100
    return final.fillna(0)

final_manager = perc_crosstabs(dataset1, 'is_manager', 'toplevel_manager_org', 'hierarchy_label', "TRUE", "FALSE")

# Function to combine columns
def combine_columns(dataset, column1, column2):
    return dataset[column1] + dataset[column2]

employee_count['E/04,E/4A,N/08,S/03'] = combine_columns(employee_count, 'E/04,N/08,S/03', 'E/4A')
employee_count['D/02,E/06,E/6A'] = combine_columns(employee_count, 'D/02,E/06', 'E/6A')
final_manager['E/04,E/4A,N/08,S/03'] = combine_columns(final_manager, 'E/04,N/08,S/03', 'E/4A')
final_manager['D/02,E/06,E/6A'] = combine_columns(final_manager, 'D/02,E/06', 'E/6A')


# Function to drop columns
def drop_columns(dataset, list):
        return dataset.drop(list, axis=1)
        
list = ['E/4A', 'E/04,N/08,S/03', 'D/02,E/06', 'E/6A']
employee_count = drop_columns(employee_count, list)

list2 = ['E/04,N/08,S/03', 'E/4A', 'D/02,E/06', 'E/6A']
final_manager = drop_columns(final_manager, list2)

# Function to reorder columns
def reorder(dataset, columns):
    return dataset[columns]

columns1 = ['N/01', 'N/02', 'N/03', 'N/04', 'E/01,N/05', 'E/02,N/06,S/01', 'E/03,N/07,S/02,E00', 'E/04,E/4A,N/08,S/03', 'E/05,S/04', 'D/01,E/5A', 'D/02,E/06,E/6A', 'D/03,E/07', 'E/7A,O/01', 'E/08,O/1A', 'O/02', 'O/03']
employee_count = reorder(employee_count, columns1)

columns2 = ['N/01', 'N/02', 'N/03', 'N/04', 'E/01,N/05', 'E/02,N/06,S/01', 'E/03,N/07,S/02,E00', 'E/04,E/4A,N/08,S/03', 'E/05,S/04', 'D/01,E/5A', 'D/02,E/06,E/6A', 'D/03,E/07', 'E/7A,O/01', 'E/08,O/1A', 'O/02', 'O/03']
final_manager = reorder(final_manager, columns2)

# Function to store columns in variables
def var(dataset):
    return dataset.columns

column_names = var(employee_count)
column_names_manager = var(final_manager)

# Function to reindex row names
def reindex(dataset, list):
    return dataset.reindex(list)

list = ['CMG', 'Corporate', 'gRED', 'PD', 'PT', 'GPS']
employee_count = reindex(employee_count, list)
final_manager = reindex(final_manager, list)


# Function to store actual values and log values both in list format
def log(dataset): 
    dataset = np.round(dataset, decimals=0)
    values = dataset.values
    log_values = ma.log10(values)
    return (log_values.filled(0)), values.tolist() 

new_values, list_values = log(employee_count)
new_values_manager, list_values_manager = log(final_manager)
