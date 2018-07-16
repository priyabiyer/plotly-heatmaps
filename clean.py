# Import packages for DASH app
import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc

# Import pandas, numpy and other packages for pull from database
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

## FUNCTION TO REPLACE CATEGORY NAMES FOR COLUMN
def rename(dataset, column, Old1, New1, Old2, New2, Old3, New3, Old4, New4, Old5, New5, Old6, New6, Old7, New7):
    return dataset[column].replace({Old1: New1, Old2: New2, Old3: New3, Old4: New4, Old5: New5, Old6: New6, Old7: New7}) 

# Initialize replacing category names for column 
dataset1['toplevel_manager_org'] = rename(dataset1, 'toplevel_manager_org', 'Pharma Global Technical Operations', 'PT', 'Commercial Operations', 'CMG', 'Corporate Groups', 'Corporate', 'Product Development', 'PD', 'Medical Affairs', 'CMG', 'Global Product Strategy', 'GPS', 'Genentech (Not mapped)', 'Not mapped')


## FUNCTION TO DROP ROWS THAT CONTAIN A COLUMN WITH SPECIFIC CATEGORIES
def drop_row(dataset, column, cat_name):
    return dataset.loc[~dataset[column].str.contains(cat_name)]

# Initialize for toplevel_manager_org and hierarchy_label
dataset1 = drop_row(dataset1, 'toplevel_manager_org', "Latin America Region")
dataset1 = drop_row(dataset1, 'toplevel_manager_org', "Roche Partnering")
dataset1 = drop_row(dataset1, 'toplevel_manager_org', "Not mapped")
dataset1 = drop_row(dataset1, 'hierarchy_label', "N/00")

# Create dataframe with cross-tabulation of # of employees in each sub-group by level
employee_count = pd.crosstab(dataset1.toplevel_manager_org, dataset1.hierarchy_label)

## FUNCTION TO CREATE DATAFRAME WITH % OF TOTAL VALUE THAT ARE X
def perc_crosstabs(dataset, column, column1_crosstab, column2_crosstab, variable1, variable2):
    newdataset1 = dataset[dataset[column] == variable1]
    newdataset2 = dataset[dataset[column] == variable2]
    new_crosstabs1 = pd.crosstab(newdataset1[column1_crosstab], newdataset1[column2_crosstab], margins=False)
    new_crosstabs2 = pd.crosstab(newdataset2[column1_crosstab], newdataset2[column2_crosstab], margins=False)
    final = (new_crosstabs1 / (new_crosstabs1 + new_crosstabs2)) * 100
    return final.fillna(0)

# Initialize function above to create dataset with % of employees who are managers
final_manager = perc_crosstabs(dataset1, 'is_manager', 'toplevel_manager_org', 'hierarchy_label', "TRUE", "FALSE")

## FUNCTION TO COMBINE COLUMNS
def combine_columns(dataset, column1, column2):
    return dataset[column1] + dataset[column2]

# Initialize function with specific columns to combine
employee_count['E/04,E/4A,N/08,S/03'] = combine_columns(employee_count, 'E/04,N/08,S/03', 'E/4A')
employee_count['D/02,E/06,E/6A'] = combine_columns(employee_count, 'D/02,E/06', 'E/6A')
final_manager['E/04,E/4A,N/08,S/03'] = combine_columns(final_manager, 'E/04,N/08,S/03', 'E/4A')
final_manager['D/02,E/06,E/6A'] = combine_columns(final_manager, 'D/02,E/06', 'E/6A')


## FUNCTION TO DROP COLUMNS
def drop_columns(dataset, list):
        return dataset.drop(list, axis=1)
        
# Initialize function with specific columns to drop
list = ['E/4A', 'E/04,N/08,S/03', 'D/02,E/06', 'E/6A']
employee_count = drop_columns(employee_count, list)

list2 = ['E/04,N/08,S/03', 'E/4A', 'D/02,E/06', 'E/6A']
final_manager = drop_columns(final_manager, list2)

## FUNCTION TO REORDER COLUMNS
def reorder(dataset, columns):
    return dataset[columns]

# Initialize function dataset and columns
columns1 = ['N/01', 'N/02', 'N/03', 'N/04', 'E/01,N/05', 'E/02,N/06,S/01', 'E/03,N/07,S/02,E00', 'E/04,E/4A,N/08,S/03', 'E/05,S/04', 'D/01,E/5A', 'D/02,E/06,E/6A', 'D/03,E/07', 'E/7A,O/01', 'E/08,O/1A', 'O/02', 'O/03']
employee_count = reorder(employee_count, columns1)

columns2 = ['N/01', 'N/02', 'N/03', 'N/04', 'E/01,N/05', 'E/02,N/06,S/01', 'E/03,N/07,S/02,E00', 'E/04,E/4A,N/08,S/03', 'E/05,S/04', 'D/01,E/5A', 'D/02,E/06,E/6A', 'D/03,E/07', 'E/7A,O/01', 'E/08,O/1A', 'O/02', 'O/03']
final_manager = reorder(final_manager, columns2)

## FUNCTION TO STORE COLUMNS IN VARIABLES
def var(dataset):
    return dataset.columns

# Initialize for employee_count and final_manager
column_names = var(employee_count)
column_names_manager = var(final_manager)

## FUNCTION TO REINDEX ROW NAMES 
def reindex(dataset, list):
    return dataset.reindex(list)

# Initialize reindex function above for employee count and manager %
list = ['CMG', 'Corporate', 'gRED', 'PD', 'PT', 'GPS']
employee_count = reindex(employee_count, list)
final_manager = reindex(final_manager, list)


## FUNCTION TO STORE ACTUAL VALUES IN LIST FORMAT AND LOG VALUES
def log(dataset): 
    dataset = np.round(dataset, decimals=0)
    values = dataset.values
    log_values = ma.log10(values)
    return (log_values.filled(0)), values.tolist() 

# Initialize function above for employee count and manager %
new_values, list_values = log(employee_count)
new_values_manager, list_values_manager = log(final_manager)

# Customize Chart 1
id1 = 'heatmap'
colorbar1 = {'title': "Employee Counts",'tickvals': [0, 3], 'ticktext':['0','1200']}
colorscale1 = 'Viridis'
type1 = 'heatmap'
height1 =  450
margin1 =  160
width1 = 600
title1 = 'Hover Over Each Square of Graph for Employee Count'

# Customize Chart 2
id2 = 'heatmap2'
colorbar2 = {'title': "Percentage of Managers",'tickvals': [0, 2], 'ticktext':['0','100']}
colorscale2 = 'Viridis'
type2 = 'heatmap'
height2 = 450
margin2 = 160
width2 = 600
title2 = "Hover Over Each Square of Graph for Percentage of Managers"

import json

app = dash.Dash()
app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Graph(id=id1, figure={'data': [{
                'z': new_values,
                'y': list,
                'x': column_names,
                'text': list_values,
                'hoverinfo': 'text',
                'colorbar': colorbar1, 
                'colorscale': colorscale1,
                'type': type1
            }],
            'layout': {
               'height': height1,
               'margin': {"b": margin1},
               'width': width1,
               'title': title1
            }
    })], className="six columns"),
        
        html.Div([
            dcc.Graph(id=id2, figure={'data': [{
                'z': new_values_manager,
                'y': list,
                'x': column_names_manager,
                'text': list_values_manager,
                'hoverinfo': 'text',
                'colorbar': colorbar2, 
                'colorscale': colorscale2,
                'type': type2
            }],
            'layout': {
               'height': height2,
               'width': width2,
               'margin': {"b": margin2},
               'title': title2
            }                                
    })], className="six columns"),
    ], className="row"),
    html.Div(id='output')
])

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

@app.callback(
    Output('output', 'children'),
    [Input('heatmap', 'hoverData'),
     Input('heatmap', 'clickData')])
def display_hoverdata(hoverData, clickData):
    return [
        json.dumps(hoverData, indent=2),
        html.Br(),
        json.dumps(clickData, indent=2)
    ]


if __name__ == '__main__':
    app.run_server(debug=True)