# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 16:28:48 2020

@author: 100008706
"""
import requests
import pandas as pd
import pickle 
import dash
import dash_core_components as dcc 	#This library will give us the dashboard elements (pie charts, scatter plots, bar graphs etc)
import dash_html_components as html 	#This library allows us to arrange the elements from dcc in a page as is done using html/css (how the internet generally does it)
import plotly.express as px
import datetime as dt

#Read Solar and Wind maintenance schedules at startup 
maintsolar = pd.read_csv('maintsolar.csv')
maintsolar["currentdate"] = dt.datetime.now().strftime('%Y-%m-%d')
maintsolar = maintsolar.rename(columns = {'Date Of Month':'day'})
maintsolar.columns = maintsolar.columns.str.replace(' ','_')
    
maintwind = pd.read_csv('maintwind.csv')
maintwind["currentdate"] = dt.datetime.now().strftime('%Y-%m-%d')
maintwind = maintwind.rename(columns = {'Date Of Month':'day'})
maintwind.columns = maintwind.columns.str.replace(' ','_')

#Create the Das server and plost using plotly express
def get_dash(server):
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__, 
                    server=server,
                    routes_pathname_prefix='/dashapp/',
                    external_stylesheets=external_stylesheets
                    )
    
    
    dfslist = solarplant()
    dfwlist = windplant()
 
    styles = get_styles()
    
    fig = px.bar(dfslist, x="date", y="Predicted_Power", color="date", barmode="group", title="4-Day Predicted Solar Energy")
    fig1 = px.bar(dfwlist, x="date", y="Predicted_Power", color="date", barmode="group", title="4-Day Predicted Wind Energy")
    
    fig2 = px.pie(dfslist, values='Predicted_Power', names='date', title="Solar Energy for the next four days")
    fig3 = px.pie(dfwlist, values='Predicted_Power', names='date', title="Wind Energy for the next four days")
    
    app.layout = html.Div([
        html.H5("The graphs below show the predicted power for the Solar plant at Malpas-Trenton, Australia and Wind plant at Klushof, Germany"),
        html.A("Go to Home Page", href="/", style=styles["button_styles"]),
        html.Div("Note that predicted power could be influenced by maintenance schedules", id='my-output',
                 style=styles["text_styles"]),
        dcc.Graph(
            id='Solar',
            figure = fig
        ),
        dcc.Graph(
            id='Wind',
            figure = fig1
        ),
        dcc.Graph(
            id='Solar1',
            figure = fig2
        ),
        dcc.Graph(
            id='Wind1',
            figure = fig3
        ),                
    ])

    return app    
    
#Function for Solar plant to collect weather information write this into a dataframe, predict power generation using RandomForestRegression and calculate true predicted power factoring in maintenance schedule
def solarplant():
    lat = ("142.15")
    lon = ("19.92")
    
    url = ("http://www.7timer.info/bin/meteo.php?lon=" + str(lon) + "&lat=" + str(lat) +"&ac=0&unit=British&output=json&tzshift=0")
        
    data = requests.get(url).json()
          
    
    temp = []
    cloud = []
    rain =[]
        
    for item in data["dataseries"]:
        temp.append(item["temp2m"])
        cloud.append(item["cloudcover"])
        rain.append(item["prec_amount"])
    
    temp = pd.DataFrame(temp, columns = ['temp_avg']) 
    cloud = pd.DataFrame(cloud, columns = ['Cloud Cover Percentage']) 
    rain = pd.DataFrame(rain, columns = ['Rainfall in mm']) 
        
    solargeneration = pd.concat([temp, cloud, rain], axis=1)
    
    fileObj = open('modelsolar.obj', 'rb')
    modelsolar = pickle.load(fileObj)
    fileObj.close()
    
    Xsolar = solargeneration[['temp_avg', 'Cloud Cover Percentage', 'Rainfall in mm']].values
    solar_predicted_power = modelsolar.predict(Xsolar)
    
    slist = solar_predicted_power.tolist()
    
    #global dfslist
    dfslist = pd.DataFrame(slist, columns = ['Predicted Power'])
    dfslist["date"] = pd.DataFrame({"date":pd.date_range(dt.datetime.now().strftime('%H:%M:%S'), periods=64, freq='3h')})
    dfslist = dfslist.resample('24h', on = 'date').mean()
    #dfslist["date"] = pd.DataFrame({"date":pd.date_range(dt.datetime.now().strftime('%H:%M:%S'))
    dfslist = dfslist.head(5)
    dfslist = dfslist.iloc[1:]
    dfslist = dfslist.reset_index()
       
    dfslist.columns = dfslist.columns.str.replace(' ','_')
    
    dfslist['day'] = pd.DatetimeIndex(dfslist['date']).day
    dfslist =dfslist.merge(maintsolar,left_on='day',right_on='day',how='left')
    dfslist = dfslist.fillna(10)
    dfslist["Predicted_Power"] = dfslist["Predicted_Power"] * dfslist["Capacity_Available"] *0.1
    
      
    return dfslist

#Function for Wind plant to collect weather information write this into a dataframe, predict power generation using RandomForestRegression and calculate true predicted power factoring in maintenance schedule
def windplant():   
    lon = ("53.56")
    lat = ("8.59")
    
    url = ("http://www.7timer.info/bin/meteo.php?lon=" +
               str(lon) + "&lat=" + str(lat)
               +"&ac=0&unit=British&output=json&tzshift=0")
        
    data = requests.get(url).json()
       
    wind =[]
            
    for item in data["dataseries"]:
        wind.append(item["wind10m"])
       
    wind = pd.DataFrame(wind)
    wind = wind.rename(columns = {'speed': 'wind speed'}, inplace = False)
    
    fileObj = open('modelwind.obj', 'rb')
    modelwind = pickle.load(fileObj)
    fileObj.close()
    
    Xwind = wind[['wind speed', 'direction']].values
    wind_predicted_power = modelwind.predict(Xwind)
    
    
    wlist = wind_predicted_power.tolist()
    
    dfwlist = pd.DataFrame(wlist, columns = ['Predicted Power'])
    dfwlist["date"] = pd.DataFrame({"date":pd.date_range(dt.datetime.now().strftime('%H:%M:%S'), periods=64, freq='3h')})
    dfwlist = dfwlist.resample('24h', on = 'date').mean()
    dfwlist = dfwlist.head(5)
    dfwlist = dfwlist.iloc[1:]
    dfwlist = dfwlist.reset_index()
    
    dfwlist.columns = dfwlist.columns.str.replace(' ','_')     
    dfwlist['day'] = pd.DatetimeIndex(dfwlist['date']).day
    dfwlist =dfwlist.merge(maintwind,left_on='day',right_on='day',how='left')
    dfwlist = dfwlist.fillna(10)
    dfwlist["Predicted_Power"] = dfwlist["Predicted_Power"] * dfwlist["Capacity_Available"] *0.1
    

    return dfwlist

#To make things look pretty   
def get_styles():
    """
    Very good for making the thing beautiful.
    """
    base_styles = {
        "text-align": "center",
        "border": "1px solid #ddd",
        "padding": "7px",
        "border-radius": "2px",
    }
    text_styles = {
        "background-color": "#eef",
        "margin": "auto",
        "width": "70%"
    }
    text_styles.update(base_styles)

    button_styles = {
        "text-decoration": "none",
    }
    button_styles.update(base_styles)

    fig_style = {
        "padding": "10px",
        "width": "80%",
        "margin": "auto",
        "margin-top": "5px"
    }
    fig_style.update(base_styles)
    return {
        "text_styles" : text_styles,
        "base_styles" : base_styles,
        "button_styles" : button_styles,
        "fig_style": fig_style,
    } 
