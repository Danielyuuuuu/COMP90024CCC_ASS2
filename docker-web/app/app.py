from dash.dependencies import Output, Input, State
# import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from flask import Flask
import pandas as pd
import dash
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import os

env_path = Path('./web-variables.env')
load_dotenv(dotenv_path=env_path, verbose=True)

ADDRESS = os.getenv("COUCHDB_ADDRESS")
PX_TOKEN = os.getenv("PXTOKEN")

from .retrieve_data_demo import get_data_summary, get_data 

px.set_mapbox_access_token(PX_TOKEN)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = Flask(__name__)


app = dash.Dash(server=server, external_stylesheets=external_stylesheets)
app.title = 'Australia & Twitter Analyse'

infodf = pd.read_csv("./zone_stats.csv",index_col=0)
geodf = pd.read_csv("./target_zones.csv",index_col=0)[["zone","center_longitude", "center_latitude"]]
mapdf = pd.merge(geodf,infodf,how='inner',on='zone')
columns = ["Zone","lon", "lat", "Overseas Rate", "Average Study Years", "Christian Ratio",\
              "Islam Ratio", "Hindo Ratio", "No-Religon Ratio", "Median Age", "Median Total FAM INC Weekly"]
mapdf.columns=columns
att = columns[3:]


corrdf = mapdf[["Zone","Overseas Rate", "Average Study Years", "Christian Ratio",\
              "Islam Ratio", "Hindo Ratio", "No-Religon Ratio", "Median Age", "Median Total FAM INC Weekly"]].corr()
corr_fig = px.imshow(corrdf,color_continuous_scale="rdbu", range_color=[-1,1], title="Background Inner Correlation")
corr_fig.update_layout({"height": 600})


information = get_data_summary(db="covid",viewType="zone",startkey=0,mode="mean")
app.layout = html.Div([
    html.Div(ADDRESS),
    html.Div(information),
    # our graph
    html.Div([
        html.Div([
            html.Div("Map Bubble Color:"),
            dcc.Dropdown(
                id='Map Color',
                options=[{'label': i, 'value': i} for i in att],
                value='Overseas Rate'
            ),
        ],
        style={'width': '25%', 'display': 'inline-block','padding': '10px 5px'}),

        html.Div([
            html.Div("Map Bubble Size:"),
            dcc.Dropdown(
                id='Map Size',
                options=[{'label': i, 'value': i} for i in att],
                value='Overseas Rate'
            ),
        ],
        style={'width': '25%', 'display': 'inline-block','padding': '10px 5px'}),

        html.Div([
            html.Div("Twitter Analyse"),
            dcc.RadioItems(
                id='crossfilter-yaxis-type2',
                options=[{'label': i, 'value': i} for i in ['Covid19', 'Vaccination', 'Historical']],
                value='Historical',
                labelStyle={'display': 'inline-block'}
            ),
            dcc.Dropdown(
                id='crossfilter-yaxis-column1',
                options=[{'label': i, 'value': i} for i in att],
                value='Life expectancy at birth, total (years)'
            ),

        ], style={'width': '39%', 'float': 'right', 'display': 'inline-block'})
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    }),

    html.Div([
        dcc.Graph(
            id='Background Map'
        )
    ], style={'width': '55%',  'display': 'inline-block', 'padding': '0 20'}),
    html.Div([
        dcc.Graph(
            id='background correlation',
            figure=corr_fig
        )
    ], style={'width': '55%',  'display': 'inline-block', 'padding': '0 20'}),
])

@app.callback(
    dash.dependencies.Output('Background Map', 'figure'),
    [dash.dependencies.Input('Map Color', 'value'),
     dash.dependencies.Input('Map Size', 'value')])
def updata_map(color, size):
    map_center = {}
    map_center["lon"] = 135
    map_center["lat"] = -32
    map_fig = px.scatter_mapbox(
        mapdf, lat="lat", lon="lon",hover_name="Zone", color=color, size=size, color_continuous_scale="redor",
        zoom=3.3, center=map_center, title="Backgroud Map"
        )
    map_fig.update_layout({"height": 700})
    return map_fig



if __name__ == '__main__':
    app.run_server(debug=True)