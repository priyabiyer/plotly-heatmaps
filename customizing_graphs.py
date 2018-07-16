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
