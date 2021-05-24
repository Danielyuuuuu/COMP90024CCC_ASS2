from dash.dependencies import Output, Input, State
# import dash_bootstrap_components as dbc
import plotly.graph_objects as go
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
##############################################
from cloudant.design_document import DesignDocument


USERNAME='admin'
PASSWORD = 'password'
URL = 'http://' + ADDRESS + ':5984/'
from cloudant.client import CouchDB
from cloudant.design_document import DesignDocument
from cloudant.view import View

class CloudantDB():
    def __init__(self,db_name,username = USERNAME,password=PASSWORD,url = URL,partition=True):
        self.client = CouchDB(USERNAME, PASSWORD, url=URL, connect=True)
        self.session = self.client.session()
        self.curDB = None
        print('Username: {0}'.format(self.session['userCtx']['name']))
        print('Databases: {0}'.format(self.client.all_dbs()))
        self.accessDB(db_name,partition=True)
    
    def accessDB(self,db_name,partition=True):
        if(db_name in self.client.all_dbs()):
            self.curDB = self.client[db_name]
        else:
            self.curDB = self.client.create_database(db_name)
            print("creating db:",db_name)
        if self.curDB.exists():
            print('Accessing db:',db_name)
    
    def add_record(self, json_record, db_name=None, key=None):
        if(key is not None and key not in self.curDB):
            json_record['_id'] = key
            self.curDB.create_document(json_record)
        elif('id' in json_record.keys()):
            hash_string = str(hash(json_record['id']))
            if(hash_string not in self.curDB):
                json_record['_id'] = hash_string
                record = json_record
                self.curDB.create_document(record)
            else:
                print("already exist")
    
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
    elif(viewType=="month"):
        view = View(ddoc, 'view_month')
    else:
        return "Does not support viewType"+viewType
    result = []
    for row in view(limit=n,reduce=False,group=False,startkey=startkey,include_docs=True)['rows']:
        result.append(row)
    return result
##############################################





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


# information = get_data_summary(db="covid",viewType="zone",startkey=0,mode="mean")
app.layout = html.Div([

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
        style={'width': '25%', 'display': 'inline-block','padding': '20px 5px'}),

        html.Div([
            html.Div("Map Bubble Size:"),
            dcc.Dropdown(
                id='Map Size',
                options=[{'label': i, 'value': i} for i in att],
                value='Overseas Rate'
            ),
        ],
        style={'width': '25%', 'display': 'inline-block','padding': '20px 5px'}),

        html.Div([html.H2("City Analytics")], style={'display': 'inline-block','margin-left' : '100px', 'margin-bottom': '10px'}),
        
        # html.Div([
        #     html.Div("Twitter Analyse"),
        #     dcc.RadioItems(
        #         id='twitter set',
        #         options=[{'label': i, 'value': i} for i in ['Covid19', 'Vaccination']],
        #         value='Covid19',
        #         labelStyle={'display': 'inline-block'}
        #     ),
        #     dcc.Dropdown(
        #         id='background analyse',
        #         options=[{'label': i, 'value': i} for i in att],
        #         value='Overseas Rate'
        #     ),
        # ], style={'width': '42%', 'float': 'right', 'display': 'inline-block'})
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)'
    }),

    html.Div([
        dcc.Graph(
            id='Background Map'
        )
    ], style={'width': '55%',  'display': 'inline-block'}),

    # html.Div([
    #     dcc.Graph(
    #         id='history analyse'
    #     )
    # ], style={'width': '43%',  'display': 'inline-block', 'padding': '0 20'}),

    html.Div([
        dcc.Graph(
            id='monthly word'
        ),
        dcc.Graph(
            id='total word'
        )
    ], style={'width': '43%',  'display': 'inline-block'}),

    html.Div([
        dcc.Graph(
            id='Scatter'
        )
    ], style={'width': '27%',  'display': 'inline-block'}),

    html.Div([
        dcc.Graph(
            id='cov line chart'
        ),
        dcc.Graph(
            id='vac line chart'
        )
    ], style={'width': '27%',  'display': 'inline-block'}), 

    html.Div([
        dcc.Graph(
            id='background correlation',
            figure=corr_fig
        )
    ], style={'width': '43%',  'display': 'inline-block'}),
])

@app.callback(    
    dash.dependencies.Output('monthly word', 'figure'),
    dash.dependencies.Input('Background Map', 'hoverData'))
def updata_word_total_chart(hoverData):
    if not hoverData:
        hoverData ={"points":[{"hovertext":"Sydney"}]}
    zone_name = hoverData["points"][0]["hovertext"]
    tmpdf = get_monthly_topwords()
    fig = px.bar(tmpdf[tmpdf["zone"]==zone_name], x='word', y='count', animation_frame="month", title="Monthly Top Words in "+zone_name)
    fig.update_layout({"height":450})
    return fig

@app.callback(
    dash.dependencies.Output('vac line chart', 'figure'),
    dash.dependencies.Input('Background Map', 'hoverData'))
def update_linechart(hoverData):
    if not hoverData:
        hoverData ={"points":[{"hovertext":"Sydney"}]}
    fig = go.Figure()
    zone_name = hoverData["points"][0]["hovertext"]
    df = convert_dict_df(vac_dict)
    tmpdf = df[df["zone"]==zone_name]
    # print(tmpdf)
    fig.add_trace(go.Scatter(x=tmpdf["date"], y=tmpdf["senti score"], mode='lines+markers'))
    fig.update_layout({"title":zone_name+" Sentimental Score(Keyword: Vaccination)", "height":340})
    return fig

@app.callback(
    dash.dependencies.Output('cov line chart', 'figure'),
    dash.dependencies.Input('Background Map', 'hoverData'))
def update_linechart(hoverData):
    if not hoverData:
        hoverData ={"points":[{"hovertext":"Sydney"}]}
    fig = go.Figure()
    zone_name = hoverData["points"][0]["hovertext"]
    df = convert_dict_df(cov_dict)
    tmpdf = df[df["zone"]==zone_name]
    fig.add_trace(go.Scatter(x=tmpdf["date"], y=tmpdf["senti score"], mode='lines+markers'))
    fig.update_layout({"title":zone_name+" Sentimental Score(Keyword: Covid)", "height":340})
    return fig

@app.callback(
    dash.dependencies.Output('total word', 'figure'),
    dash.dependencies.Input('Background Map', 'hoverData'))
def update_linechart(hoverData):
    if not hoverData:
        hoverData ={"points":[{"hovertext":"Sydney"}]}
    fig = go.Figure()
    zone_name = hoverData["points"][0]["hovertext"]

    df = convert_count(wordfreq)
    tmpdf = df[df["zone"]==zone_name]

    fig = px.bar(tmpdf, y='count', x='word')
    # fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(uniformtext_minsize=8, title="Top Word History", uniformtext_mode='hide', height=250)

    return fig


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

@app.callback(
    dash.dependencies.Output('Scatter', 'figure'),
     dash.dependencies.Input('Map Size', 'value'))
def updata_map(size):

    sendf = pd.DataFrame(sen_withoutzone.items())
    sendf.columns = ["zone", "sen score"]
    pd.merge(sendf,mapdf,how='inner',on='zone')

    fig = px.scatter(mapdf, x=size, y="sen score",title="History Sentiment by "+size)
    fig.update_layout({"height": 700})
    return fig


def convert_monthly_topword(monthly_topword):
    lst = []
    for month in monthly_topword:
        for area in monthly_topword[month]:
            for word in monthly_topword[month][area]:
                lst.append([month, area, word, monthly_topword[month][area][word]])
    
    return pd.DataFrame(lst)



cov_dict = get_data_summary(db="covid",viewType="zone month")

vac_dict = get_data_summary(db="vaccine",viewType="zone month")

wordfreq = {"Adelaide": {"Adelaide": 281, "Australia": 203, "South": 163, "posted": 141, "photo": 134, "today": 125, "people": 82, "great": 80, "Happy": 68, "video": 68}, "Ballarat": {"#walkies": 24, "Ballarat": 23, "Abstract": 16, "#zerowaste": 14, "#recycle": 13, "#MAFS": 12, "#abstractart": 12, "#artist": 11, "#recycling": 11, "#artwork": 11}, "Brisbane": {"posted": 961, "photo": 938, "Brisbane": 489, "Queensland": 476, "Australia": 350, "today": 201, "people": 126, "great": 119, "night": 114, "first": 111}, "Bunbury": {"Bunbury": 7, "Western": 4, "Australia": 4, "posted": 3, "photo": 3, "#housesitting": 2, "walking": 2, "today": 2, "Taking": 1, "break": 1}, "Canberra": {"Canberra": 168, "posted": 101, "photo": 97, "Australian": 71, "Australia": 65, "great": 58, "eWasp": 58, "today": 55, "people": 52, "morning": 50}, "Geelong": {"Geelong": 80, "Extreme": 44, "Board": 37, "Store": 25, "Victoria": 24, "today": 22, "Tours": 17, "photo": 16, "posted": 15, "WARRIORS": 13}, "Hobart": {"Tasmania": 58, "Australia": 43, "Hobart": 39, "Kingston": 33, "photo": 33, "posted": 32, "Beach": 30, "today": 23, "iPhone": 20, "#blackandwhite": 19}, "Melbourne": {"posted": 2452, "photo": 2270, "Victoria": 1343, "Melbourne": 1336, "Australia": 1137, "today": 539, "people": 410, "great": 385, "would": 323, "video": 300}, "Newcastle": {"posted": 251, "photo": 226, "Newcastle": 188, "South": 90, "Wales": 89, "Forum": 76, "University": 69, "Sport": 61, "today": 51, "Australia": 37}, "Perth": {"Perth": 479, "Australia": 474, "posted": 453, "photo": 415, "Western": 414, "today": 153, "people": 129, "@11AberdeenStreet": 124, "\ufe0f0893252011": 116, "great": 109}, "Sydney": {"posted": 3089, "photo": 2893, "Sydney": 2420, "Australia": 2182, "South": 633, "Wales": 588, "today": 582, "people": 368, "great": 364, "video": 348}}
sen_withoutzone = {'Adelaide': 0.693848,
                'Ballarat': 0.715091,
                'Brisbane': 0.710385,
                'Bunbury': 0.80026,
                'Canberra': 0.690317,
                'Geelong': 0.678222,
                'Hobart': 0.690671,
                'Melbourne': 0.704503,
                'Newcastle': 0.75033,
                'Perth': 0.700816,
                'Sydney': 0.723348}

def get_monthly_topwords():
    db10 = CloudantDB("monthlytopwords")
    data = db10.get_data()
    lst = []

    for month_data in data:
        month = month_data["_id"]
        for key in month_data:
            if key != "_id" and key!= "_rev":
                for word in month_data[key]:
                    count = month_data[key][word]
                    lst.append([month, key, word, count])
    df = pd.DataFrame(lst)
    df.columns = ["month", "zone", "word", "count"]
    return df


def convert_sen_df(sen_dict):
    sen_list = []
    for i in sen_dict:
        sen_list.append([i, sen_dict[i]])
    sen_df = pd.DataFrame(sen_list)
    sen_df.columns = ["zone", "senti score"]
    return sen_df

def convert_count(wordfreq):
    lst = []
    for i in wordfreq:
        area_count = wordfreq[i]
        for j in area_count:
            lst.append([i, j, area_count[j]])
    df = pd.DataFrame(lst)
    df.columns = ["zone", "word", "count"]
    return df

def convert_dict_df(sen_dict):
    sen_list = []
    for i in sen_dict:
        date, zone = i.split(" ")
        sen_list.append([date, zone, sen_dict[i]])

    sen_df = pd.DataFrame(sen_list)
    sen_df.columns = ["date", "zone", "senti score"]
    return sen_df

if __name__ == '__main__':
    app.run_server(debug=True)