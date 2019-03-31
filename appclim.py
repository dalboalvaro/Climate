# import dependencies 
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Database Engine
engine = create_engine("sqlite:///Resources/Hawaii.sqlite")
# reflect the database 
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Classes
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create session (link) to the DB
session = Session(engine)

# Create an app, being sure to pass __name__
app = Flask(__name__)

# Routes
@app.route("/")
def welcome():
    session = Session(engine)    
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- Precipitation from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- List of Stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- Temperatures from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/start<br/>"
        f"- Given start date (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature for all dates greater than and equal to the start date<br/>"
        f"<br/>"
        f"/api/v1.0/start/end<br/>"
        f"- Given start and end date (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for dates between the start and end date inclusive<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)    
#    Query for the dates and precipitation observations from the last year.
#    Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
#    Return the json representation of your dictionary.
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    rain = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > one_year_ago).\
        order_by(Measurement.date).all()

# Create a list of dicts with `date` and `prcp` as the keys and values
    rain_totals = []
    for result in rain:
        row = {}
        row["date"] = rain[0]
        row["prcp"] = rain[1]
        rain_totals.append(row)

    return jsonify(rain_totals)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations_query = session.query(Station.name, Station.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    return jsonify(stations.to_dict())

@app.route("/api/v1.0/tobs")
def tobs():
    
#    Query for the dates and temperature observations from the last year.
#    Convert the query results to a Dictionary using `date` as the key and `tobs` as the value.
#    Return the json representation of your dictionary.
    session = Session(engine)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temperature = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > one_year_ago).\
        order_by(Measurement.date).all()

# list with `date` and `tobs` as keys and values
    temperature_totals = []
    for result in temperature:
        row = {}
        row["date"] = temperature[0]
        row["tobs"] = temperature[1]
        temperature_totals.append(row)

    return jsonify(temperature_totals)

@app.route("/api/v1.0/<start>")
def trip1(start):

 # Min/Avg/Max temp during time range 
    session = Session(engine)
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    one_year_ago = dt.timedelta(days=365)
    start = start_date-one_year_ago
    end =  dt.date(2017, 8, 23)
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

@app.route("/api/v1.0/<start>/<end>")
def trip2(start,end):

  # temp during time range     
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    one_year_ago = dt.timedelta(days=365)
    start = start_date-one_year_ago
    end = end_date-one_year_ago
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)


if __name__ == "__main__":
    app.run(debug=True)
