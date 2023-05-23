# Import the dependencies.
from flask import Flask, jsonify
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///../Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    text = ["Your options for routes are the following:", "/api/v1.0/precipitation:  Show statistical data based on the previous year of precipitation.","/api.v1.0/stations:  Lists all the stations used for recording data.","/api/v1.0/tobs:  Gives the dates and temperatures for the most active station of the past year.","/api/v1.0/<start>:  Gives the minimum, maximum, and average temperatures after a specified date (Use yyyy-mm-dd format).","/api/v1.0/<start>/<end>:  Gives the minimum, maximum, and average temperatures between two specified dates (Use yyyy-mm-dd format)."]
    return jsonify(text)

@app.route("/api/v1.0/precipitation")
def precipitation():

    latest = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    starting_date = (dt.datetime.strptime(latest[0],"%Y-%m-%d") - dt.timedelta(days=365)).strftime("%Y-%m-%d")

    data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= starting_date).all()

    df = pd.DataFrame(data,columns = ["date","prcp"])

    date = df["date"].tolist()

    prcp = df["prcp"].tolist()

    my_dict = {}

    for i in range(0,len(date)):
        my_dict[date[i]] = prcp[i]

    return jsonify(my_dict)

@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.station)
    station_list = []
    for i in stations:
        station_list.append(i[0])
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():

    latest = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    starting_date = (dt.datetime.strptime(latest[0],"%Y-%m-%d") - dt.timedelta(days=365)).strftime("%Y-%m-%d")

    data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= starting_date).all()

    my_list = []

    for i in data:
        my_dict = {i[0]:i[1]}
        my_list.append(my_dict)

    return jsonify(my_list)

@app.route("/api/v1.0/<start>")
def start(start):

    avg = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start)

    min = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start)

    max = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start)

    my_dict = {"Minimum":min[0][0], "Average":avg[0][0], "Maximum":max[0][0]}

    return jsonify(my_dict)

@app.route("/api/v1.0/<start>/<end>")
def end(start, end):

    avg = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end)

    min = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end)

    max = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end)

    my_dict = {"Minimum":min[0][0], "Average":avg[0][0], "Maximum":max[0][0]}

    return jsonify(my_dict)

if __name__ == "__main__":
    app.run(debug=True)