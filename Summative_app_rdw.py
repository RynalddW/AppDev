# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 16:26:26 2020

@author: 100008706
"""
#Import all required modules
import flask
import Summative_dashboard_rdw
from twilio.rest import Client

#Import Solar and Wind plant predicted forecasts
from Summative_dashboard_rdw import solarplant, windplant

#Prepare Predicted data to be send via SMS :
dfslist = solarplant()
dfwlist = windplant()

dfslist.drop(['date', 'Capacity_Available', 'currentdate'],  axis=1, inplace=True)
dfwlist.drop(['date', 'Capacity_Available', 'currentdate'],  axis=1, inplace=True)


dfsdict = dfslist.to_string()
dfwdict = dfwlist.to_string()

#Initiate Flask and Dash server
server = flask.Flask(__name__)
app = Summative_dashboard_rdw.get_dash(server)


#Define route and endpoints 

@app.server.route("/", methods=["GET"])
def index():
    return flask.render_template("index.html")

#Upload solar plant maintenance file 
@app.server.route("/maint_solar", methods=["POST"])
def store_solar():
    #storing the file here
    file_obj = flask.request.files.get("filename", None)
    
    file_obj.save("maintsolar.csv")
    return flask.redirect("/")

#Upload wind plant maintenance file
@app.server.route("/maint_wind", methods=["POST"])
def store_wind():
    #storing the file here
    file_obj = flask.request.files.get("filename", None)
    
    file_obj.save("maintwind.csv")
    return flask.redirect("/")
           
#Sending SMS messages uing twilio API 
@app.server.route("/sms", methods=["GET"])
def sms_url():
    
    #message = sms.values.tolist()
    #print(message)
    # Your Account Sid and Auth Token from twilio.com/console
    # DANGER! This is insecure. See http://twil.io/secure
    account_sid = 'ACc8f44f0da4ebe10b9b0a4a6a1e7c041e'
    auth_token = '1a9e2acac6a5f1f0448e368ac5aac07b'
    client = Client(account_sid, auth_token)
    
    message = client.messages \
                    .create(
                         body=("Solar:" + " " + dfsdict + " " + "Wind:" + " " + dfwdict),
                         from_='+1 773 900 5785',
                         to='+27664727789'
                     )

    return flask.redirect("/")

if __name__ == '__main__':
    app.run_server(port=5001, debug=False)