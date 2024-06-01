from flask import Flask, render_template,request,redirect
import pandas as pd
import shapely.geometry
app =  Flask(__name__)
import base64, json

@app.route('/',methods=['GET','POST'])
def index():
    if request.method =="POST":
        phone_number = request.form['number']
        state = request.form['states']
        carrier = request.form['carrier']
        lat = request.form['userLat']
        lon = request.form['userLon']
        register(phone_number,state,carrier,lat,lon)
    return render_template('index.html')


def register(number,state,carrier,lat,lon):
    df = pd.read_csv('users.csv')
    for row in df.iterrows():
        if row[1]['number'] == number:
            return render_template('index.html')
    newEntry = {
        'number':[number],
        'carrier':[carrier],
        'state':[state],
        'latPos':[lat],
        'lonPos':[lon]
    }
    newEntryDf = pd.DataFrame(newEntry)
    df = pd.concat([df,newEntryDf],ignore_index=True)
    df.to_csv('users.csv',index=False)


@app.route('/alert',methods=['GET','POST'])
def alertCheck():
    try:
        status = ""
        base64_stuff = request.args.get('data')
        json_stuff = base64.urlsafe_b64decode(base64_stuff).decode()
        data = json.loads(json_stuff)
        if request.method =="POST":
            userLat = request.form['userLat']
            userLon = request.form['userLon']
            pointsList = []
            for coord in data['polygon'][0]:
                pointsList.append(shapely.geometry.Point(coord))
            polyShape = shapely.geometry.Polygon(pointsList)   
    
            if checkWithin(polyShape,userLat,userLon):
                status = "true"
            else:
                status = "false"
        return render_template("alert.html",statusDisplay = status,contents = data)
    except:
        return redirect('badRequest')
def checkWithin(polygon,userLat,userLon):
    pointUser = shapely.geometry.Point(userLon,  userLat)
    return pointUser.within(polygon)

@app.route('/badRequest')
def unableToProcess():
    return "Bad URL. Check to ensure the provided URL is correct.",400
if __name__ == '__main__':
    app.run(debug=True)