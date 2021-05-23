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
                id='twitter set',
                options=[{'label': i, 'value': i} for i in ['Covid19', 'Vaccination']],
                value='Covid19',
                labelStyle={'display': 'inline-block'}
            ),
            dcc.Dropdown(
                id='background analyse',
                options=[{'label': i, 'value': i} for i in att],
                value='Overseas Rate'
            ),
        ], style={'width': '42%', 'float': 'right', 'display': 'inline-block'})
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

    # html.Div([
    #     dcc.Graph(
    #         id='history analyse'
    #     )
    # ], style={'width': '43%',  'display': 'inline-block', 'padding': '0 20'}),

    html.Div([
        dcc.Graph(
            id='topic'
            
        ),
        dcc.Graph(
            id='line chart'
        )
    ], style={'width': '43%',  'display': 'inline-block', 'padding': '0 20'}),

    html.Div([
        dcc.Graph(
            id='Scatter'
        )
    ], style={'width': '55%',  'display': 'inline-block', 'padding': '0 20'}),

    html.Div([
        dcc.Graph(
            id='background correlation',
            figure=corr_fig
        )
    ], style={'width': '43%',  'display': 'inline-block', 'padding': '0 20'}),

])

@app.callback(
    dash.dependencies.Output('line chart', 'figure'),
    [dash.dependencies.Input('Background Map', 'hoverData'),
     dash.dependencies.Input('twitter set', 'value')])
def update_linechart(hoverData, dataset):
    if not hoverData:
        hoverData ={"points":[{"hovertext":"Sydney"}]}
    fig = go.Figure()
    zone_name = hoverData["points"][0]["hovertext"]
    if dataset == "Covid19":
        df = convert_dict_df(cov_dict)
    elif dataset == "Vaccination":
        df = convert_dict_df(vac_dict)

    tmpdf = df[df["zone"]==zone_name]
    # print(tmpdf)
    fig.add_trace(go.Scatter(x=tmpdf["date"], y=tmpdf["senti score"], mode='lines+markers'))
    fig.update_layout({"title":zone_name+" Sentimental Score", "height":340})
    return fig

@app.callback(
    dash.dependencies.Output('topic', 'figure'),
    [dash.dependencies.Input('Background Map', 'hoverData'),
     dash.dependencies.Input('twitter set', 'value')])
def update_linechart(hoverData, dataset):
    if not hoverData:
        hoverData ={"points":[{"hovertext":"Sydney"}]}
    fig = go.Figure()
    zone_name = hoverData["points"][0]["hovertext"]

    # if dataset == "Covid19":
    #     df = convert_dict_df(cov_dict)
    # elif dataset == "Vaccination":
    #     df = convert_dict_df(vac_dict)

    df = convert_count(wordfreq)
    tmpdf = df[df["zone"]==zone_name]

    fig = px.bar(tmpdf, y='count', x='word')
    # fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', height=340)

    return fig



# @app.callback(
#     dash.dependencies.Output('history analyse', 'figure'),
#     dash.dependencies.Input('background analyse', 'value'))
# def updata_background_analyse(color, size):
#     map_center = {}
#     map_center["lon"] = 135
#     map_center["lat"] = -32
#     map_fig = px.scatter_mapbox(
#         mapdf, lat="lat", lon="lon",hover_name="Zone", color=color, size=size, color_continuous_scale="redor",
#         zoom=3.3, center=map_center, title="Backgroud Map"
#         )
#     map_fig.update_layout({"height": 300})
#     return map_fig

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
    [dash.dependencies.Input('Map Color', 'value'),
     dash.dependencies.Input('Map Size', 'value')])
def updata_map(color, size):
    # df = convert_sen_df(sen_withoutzone)
    # tmpdf = pd.merge(df,infodf,how='inner',on='zone')

    fig = px.scatter(mapdf, x=size, y=color,title="History Scatter with Sentiment")
    fig.update_layout({"height": 700})
    return fig


cov_dict = {'2020-10 Canberra': 0.428967,
 '2020-10 Melbourne': 0.633748,
 '2020-10 Sydney': 0.585607,
 '2020-11 Adelaide': 0.720719,
 '2020-11 Ballarat': 0.959367,
 '2020-11 Brisbane': 0.090615,
 '2020-11 Melbourne': 0.62116,
 '2020-11 Newcastle': 0.873696,
 '2020-11 Perth': 0.916552,
 '2020-11 Sydney': 0.472093,
 '2020-12 Adelaide': 0.5908,
 '2020-12 Canberra': 0.7206,
 '2020-12 Melbourne': 0.804355,
 '2020-12 Newcastle': 0.797671,
 '2020-12 Perth': 0.770182,
 '2020-12 Sydney': 0.646368,
 '2021-01 Adelaide': 0.881215,
 '2021-01 Brisbane': 0.572534,
 '2021-01 Geelong': 0.956574,
 '2021-01 Melbourne': 0.655604,
 '2021-01 Newcastle': 0.870344,
 '2021-01 Perth': 0.693467,
 '2021-01 Sydney': 0.522584,
 '2021-02 Adelaide': 0.560757,
 '2021-02 Ballarat': 0.507445,
 '2021-02 Brisbane': 0.380608,
 '2021-02 Bunbury': 0.638711,
 '2021-02 Melbourne': 0.61499,
 '2021-02 Newcastle': 0.850101,
 '2021-02 Perth': 0.576656,
 '2021-02 Sydney': 0.532095,
 '2021-03 Adelaide': 0.738264,
 '2021-03 Brisbane': 0.55058,
 '2021-03 Canberra': 0.209001,
 '2021-03 Geelong': 0.481629,
 '2021-03 Hobart': 0.719436,
 '2021-03 Melbourne': 0.620685,
 '2021-03 Newcastle': 0.716539,
 '2021-03 Perth': 0.837277,
 '2021-03 Sydney': 0.703736,
 '2021-04 Adelaide': 0.405339,
 '2021-04 Ballarat': 0.97662,
 '2021-04 Brisbane': 0.678456,
 '2021-04 Bunbury': 0.737654,
 '2021-04 Canberra': 0.345909,
 '2021-04 Geelong': 0.642872,
 '2021-04 Hobart': 0.301131,
 '2021-04 Melbourne': 0.533369,
 '2021-04 Newcastle': 0.921058,
 '2021-04 Perth': 0.456338,
 '2021-04 Sydney': 0.473733,
 '2021-05 Adelaide': 0.575753,
 '2021-05 Brisbane': 0.542839,
 '2021-05 Canberra': 0.617221,
 '2021-05 Geelong': 0.499726,
 '2021-05 Hobart': 0.76256,
 '2021-05 Melbourne': 0.536976,
 '2021-05 Newcastle': 0.439819,
 '2021-05 Perth': 0.613703,
 '2021-05 Sydney': 0.526603}

vac_dict = {'2020-12 Brisbane': 0.567506,
 '2020-12 Melbourne': 0.319839,
 '2021-01 Melbourne': 0.973089,
 '2021-01 Perth': 0.469999,
 '2021-01 Sydney': 0.905628,
 '2021-02 Adelaide': 0.899132,
 '2021-02 Melbourne': 0.582535,
 '2021-02 Sydney': 0.62045,
 '2021-03 Adelaide': 0.566033,
 '2021-03 Canberra': 0.101422,
 '2021-03 Hobart': 0.473581,
 '2021-03 Melbourne': 0.60924,
 '2021-03 Perth': 0.705826,
 '2021-03 Sydney': 0.51967,
 '2021-04 Adelaide': 0.541486,
 '2021-04 Brisbane': 0.567416,
 '2021-04 Canberra': 0.646087,
 '2021-04 Geelong': 0.285157,
 '2021-04 Melbourne': 0.491468,
 '2021-04 Perth': 0.617063,
 '2021-04 Sydney': 0.597414,
 '2021-05 Adelaide': 0.492799,
 '2021-05 Brisbane': 0.54124,
 '2021-05 Canberra': 0.559761,
 '2021-05 Geelong': 0.620549,
 '2021-05 Hobart': 0.308682,
 '2021-05 Melbourne': 0.523552,
 '2021-05 Newcastle': 0.665563,
 '2021-05 Perth': 0.512675,
 '2021-05 Sydney': 0.525757}

wordfreq = {"Geelong": {"Avalon": 142, "Timeline": 115, "Yangs": 88, "today": 82, "would": 80, "Victoria": 80, "follow": 65, "Australia": 63, "Werribee": 59, "think": 54, "Melbourne": 54}, "Melbourne": {"Melbourne": 54672, "today": 44645, "Humidity": 37364, "Barometer": 37325, "Temperature": 35466, "slowly": 23294, "Victoria": 21261, "#Melbourne": 21058, "Falling": 16886, "Rising": 16864, "Australia": 16330}, "Perth": {"Perth": 46422, "Australia": 29833, "Western": 22620, "today": 12782, "#perth": 9368, "#Perth": 8962, "photo": 7031, "night": 6561, "posted": 6496, "great": 6041, "Fremantle": 6004}, "Brisbane": {"Brisbane": 71337, "Queensland": 27375, "Australia": 23794, "station": 23525, "METAR": 18177, "There": 17952, "0/000": 17182, "#Brisbane": 16456, "#brisbane": 14022, "today": 12095, "photo": 10200}, "Sydney": {"Sydney": 172956, "Hotel": 94465, "#nowplaying": 86101, "Parramatta": 74094, "Australia": 72755, "Collector": 70019, "#Sydney": 55986, "Download": 55791, "#sydney": 39656, "today": 36782, "Beach": 31532}, "Hobart": {"Hobart": 4639, "Tasmania": 3778, "#tasmania": 1389, "photo": 1161, "#hobart": 1148, "posted": 1126, "Australia": 847, "today": 637, "Wellington": 615, "Museum": 498, "@Altiusrt": 466}, "Canberra": {"Canberra": 22035, "carrier": 17839, "Frequency": 17833, "strength": 17816, "Signal": 17739, "receiving": 17378, "#Canberra": 8215, "Australian": 7930, "TURBO": 7909, "Capital": 5942, "#canberra": 5049}, "Newcastle": {}, "Adelaide": {"Adelaide": 41981, "Australia": 20720, "South": 18595, "#Adelaide": 9401, "#adelaide": 7184, "today": 6708, "photo": 6417, "posted": 5778, "night": 5608, "morning": 5232, "Drinking": 5189}, "Bunbury": {}, "Ballarat": {}}
sen_withoutzone = {"Brisbane": 0.5817642194444445, "Sydney": 0.6022361873333333, "Melbourne": 0.55994314655, "Adelaide": 0.6546574548571428, "Hobart": 0.67630666, "Perth": 0.5138315539999999, "Ballarat": 0.9766196, "Newcastle": 0.64645645275, "Canberra": 0.329503115}
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