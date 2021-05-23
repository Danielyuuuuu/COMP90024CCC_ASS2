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


####################################################
USERNAME='admin'
PASSWORD = 'password'
URL = 'http://172.26.131.97:5984'
from cloudant.client import CouchDB
from cloudant.design_document import DesignDocument
from cloudant.view import View

class CloudantDB():
    def __init__(self,db_name,username = USERNAME,password=PASSWORD,url = URL):
        self.client = CouchDB(username, password, url=url, connect=True)
        self.session = self.client.session()
        self.curDB = None
        print('Username: {0}'.format(self.session['userCtx']['name']))
        print('Databases: {0}'.format(self.client.all_dbs()))
        self.accessDB(db_name)
    
    def accessDB(self,db_name):
        if(db_name in self.client.all_dbs()):
            self.curDB = self.client[db_name]
        else:
            self.curDB = self.client.create_database(db_name)
            print("creating db:",db_name)
        if self.curDB.exists():
            print('Accessing db:',db_name)
    
    def add_record(self, json_record, db_name=None):
        hash_string = str(hash(json_record['id']))
        if(hash_string not in self.curDB):
            json_record['_id'] = hash_string
            record = json_record
            my_document = self.curDB.create_document(record)
            #if my_document.exists():
                #print('Adding record...SUCCESS!!')
        else:
            print("already exist")
    
    def update_record(self, recordID, data):
        if(recordID in self.curDB):
            doc = self.curDB(recordID)
            for k,v in data.items():
                doc[k]=v
            doc.save()
            return
        hash_string = str(hash(recordID))
        if(hash_string in self.curDB):
            doc = self.curDB(hash_string)
            for k,v in data.items():
                doc[k]=v
            doc.save()
            return
        else:
            print("record not found")
    
    def delete_record(self,recordID):
        if(recordID in self.curDB):
            my_document = self.curDB[recordID]
            my_document.delete()
        elif(str(hash(recordID)) in self.curDB):
            my_document = self.curDB[str(hash(recordID))]
            my_document.delete()
        else:
            print("deletion err, record not found")
    def delete_all_records(self):
        for doc in self.curDB:
            doc.delete()
    
    def deleteDB(self,db_name):
        self.client.delete_database(db_name)
        self.curDB = None
        print(db_name,"removed")
    
    def get_data(self,n=10000):
        data = []
        count = 0
        for document in self.curDB:
            data.append(document)
            count+=1
            if(count>n):
                break
        return data
    
    def get_num_records(self):
        return len(self.curDB)
    
    def close(self):
        self.client.disconnect()
        
    def allDB(self):
        all_dbs = self.client.all_dbs()
        print('Databases: {0}'.format(all_dbs))
        return all_dbs

def get_data_summary(db="covid",viewType="month",startkey="2020-10",mode = "mean"):
    if(db=="covid"):
        db = CloudantDB('tweets_covid')
    elif(db=="vaccine"):
        db= CloudantDB("tweets_vaccine")
    elif(db=="no_keywords"):
        db=CloudantDB('tweets_no_keywords')
    else:
        print("db parameter must in [covid,vaccine,no_keywords]")
        return {}
    ddoc = DesignDocument(db.curDB,'_design/ddoc001')
    ddoc.fetch()
    if(viewType=="month"):
        view = View(ddoc, 'view_month')
    elif(viewType=="zone"):
        view = View(ddoc,"view_zone")
    elif(viewType=="zone month"):
        view=View(ddoc, 'view_zone_month')
    else:
        view = View(ddoc, 'view_time')
    result = {}
    for row in view(limit=100,reduce=True,group=True,startkey=startkey)['rows']:
        if(mode=="mean"):
            result[row['key']] = round(row['value']['sum']/row['value']['count'],6)
        elif(mode=="count"):
            result[row['key']] = row['value']['count']
    return result

def get_data(n=100,db="covid",viewType="day",startkey="2021-05-01"):
    if(db=="covid"):
        db = CloudantDB('tweets_covid')
    elif(db=="vaccine"):
        db= CloudantDB("tweets_vaccine")
    elif(db=="no_keywords"):
        db=CloudantDB('tweets_no_keywords')
    else:
        print("db parameter must in [covid,vaccine,no_keywords]")
        return []
    ddoc = DesignDocument(db.curDB,'_design/ddoc001')
    ddoc.fetch()
    if(viewType=="zone"):
        view = View(ddoc,"view_zone")
    elif(viewType=="day"):
        view = View(ddoc, 'view_time')
    else:
        return "Does not support viewType"+viewType
    result = []
    for row in view(limit=n,reduce=False,group=False,startkey=startkey,include_docs=True)['rows']:
        result.append(row)
    return result

##############################################


env_path = Path('./web-variables.env')
load_dotenv(dotenv_path=env_path, verbose=True)

ADDRESS = os.getenv("COUCHDB_ADDRESS")
PX_TOKEN = os.getenv("PXTOKEN")


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







# -*- coding: utf-8 -*-
"""
Created on Wed May 19 00:40:53 2021

@author: Windwalker
"""

if __name__ == '__main__':
    app.run_server(debug=True)