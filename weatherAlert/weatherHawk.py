import requests, time
from datetime import timezone,timedelta, datetime as dt
import pandas as pd
from dateutil import  parser
import pytz
import base64, json, urllib.parse
from notify import send_message
import shapely.geometry

stateStatus = []
discardedAlerts = []
firstIteration = True

def sendAlerts():
    print("STATES: "+str(len(stateStatus)))
    print("Entering sendAlerts()")
    global firstIteration
    users = pd.read_csv('users.csv')
    for state in stateStatus:
        if state['numAlerts']>0:
            users_in_state = users.query('state=="'+str(state['state'])+'"')
            for alert in state['alerts']:
                link = 'http://127.0.0.1:5000/alert'
                json_data = json.dumps(alert)
                data_to_base64 = base64.urlsafe_b64encode(json_data.encode()).decode()
                link = 'http://127.0.0.1:5000/alert?data='+data_to_base64
                message = str(alert['event'])+":\n Status: "+str(alert['urgency'])+"\n "+str(alert['headline'])+"\n CLICK HERE TO SEE ADDITIONAL DETAILS AND IF YOUR LOCATION IS IMPACTED: "+str(link)
                if firstIteration==True:
                    for user in users_in_state.iterrows():
                        if user[1]['latPos']!="" and user[1]['lonPos']!="" and checkLocation(alert['polygon'],user[1]['latPos'],user[1]['lonPos']):
                            print("Number:" +str(user[1]['number'])) ## supplement sending msg for now
                            print("State: "+str(user[1]['state']))
                            print("Message: "+message)
                            # send_message(str(user[1]['number']),str(user[1]['carrier']),message)
                            time.sleep(2)
                        else:
                            print("not in warned zone")
                discardedAlerts.append(alert)
            cleared_state_info = {
            'state':str(state),
            'numAlerts':0,
            'alerts':[]
            }
    stateStatus.clear()
    firstIteration = False
    # print("AFTER CLEAR: "+str(stateStatus))
    clearDiscard()

              
# sendAlerts()
def checkStates():
    print("Entering checkStates()")
    states = [
    # https://en.wikipedia.org/wiki/List_of_states_and_territories_of_the_United_States#States.
    "AK", "AL", "AR", "AZ", "CA", "CO", "CT", "MD",
    "DE", "FL", "GA", "HI", "IA",
    "ID", "IL", "IN", "KS", "KY", "LA", "MA",
    "ME", "MI", "MN", "MO",
    "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK",
    "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI",
    "WV", "WY",
    # # https://en.wikipedia.org/wiki/List_of_states_and_territories_of_the_United_States#Federal_district.
    "DC",
    # # https://en.wikipedia.org/wiki/List_of_states_and_territories_of_the_United_States#Inhabited_territories.
    "AS", "GU", "MP", "PR", "VI",
]
    
    for state in states:
        url = 'https://api.weather.gov/alerts/active?area='+str(state)+''
        request = requests.get(url)
        response = request.json()
        numAlerts = len(response['features'])
        alerts = []
        if numAlerts>0:
            for alertEntry in response['features']:
                if alertEntry['properties']['event']!="Test Message" and alertEntry['properties']['urgency']=='Immediate' and (alertEntry['properties']['event']=='Tornado Warning' or alertEntry['properties']['event']=='Flood Warning' or alertEntry['properties']['event']=='Severe Thunderstorm Warning'):
                    if alertEntry['geometry']!=None:
                        coords =  alertEntry['geometry']['coordinates']
                    else:
                        coords = None
                    alert = {
                        'effective':alertEntry['properties']['effective'],
                        'expiration':alertEntry['properties']['expires'],
                        'urgency':alertEntry['properties']['urgency'],
                        'event':alertEntry['properties']['event'],
                        'senderName':alertEntry['properties']['senderName'],
                        'headline':alertEntry['properties']['headline'],
                        'desc':alertEntry['properties']['description'],
                        'instruction':alertEntry['properties']['instruction'],
                        'polygon':coords
                    }
                    if alert not in discardedAlerts and not checkExpiration(alert['expiration']):
                        alerts.append(alert)
                        print("**New Alert Added For "+str(state)+"**")
                        print("ALERT CONTENT: "+str(alert))
                    else:
                        print("No New Alerts For "+str(state))
                        numAlerts = 0
        stateInfo = {
                            'state':str(state),
                            'numAlerts':numAlerts,
                            'alerts':alerts

                        }
        stateStatus.append(stateInfo)
        print("Sleeping...")
        time.sleep(1)
    sendAlerts()




def clearDiscard():
    print("Entering clearDiscard()")
    for discard in discardedAlerts:
        if discard['expiration']!=None:
            if(checkExpiration(discard['expiration'])):
                print("An alert was cleared!")
                print("sent by: "+str(discard['senderName']))
                discardedAlerts.remove(discard)
    
    checkStates()

def checkExpiration(expire_time_raw):
    current_time = dt.now(pytz.utc)
    expire_time = parser.parse(expire_time_raw).astimezone(pytz.utc)
    return expire_time < current_time

def checkLocation(polyCoords,userLat,userLon):
    pointsList = []
    for coord in polyCoords[0]:
        pointsList.append(shapely.geometry.Point(coord))
    polyShape = shapely.geometry.Polygon(pointsList)   
    userPoint = shapely.geometry.Point(userLon,userLat)

    return userPoint.within(polyShape)


##start func
checkStates()
# ZERO = timedelta(0)
# # "2024-05-21T03:00:00-04:00"
# notActCurr = dt(2024,5,21,7,0,0,tzinfo=timezone.utc)
# expire_time = parser.parse("2024-05-21T03:00:00-04:00").astimezone(pytz.utc)
# randoTime = dt(2024,5,21,3,42,55,0,tzinfo=timezone.utc)
# print(expire_time<notActCurr)