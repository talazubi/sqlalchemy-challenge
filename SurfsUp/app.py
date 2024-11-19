# Import the dependencies.
import datetime as dt
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify 

#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base= automap_base()

# reflect the tables
Base.prepare(autoload_with = engine) 

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement


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
def homepage():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    ) 
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Find the most recent date in the data set.
    most_recent_date = session.query(func.max(Measurement.date)).scalar() 
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
# Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= query_date).all()
    session.close()
    # Coverting the query results to a dictionary using date as key and prcp as value
    precipitation_results = []
    for date, prcp in results:
        precipitation_d = {}
        precipitation_d["date"] = date
        precipitation_d["prcp"] = prcp

        precipitation_results.append(precipitation_d)
    return jsonify(precipitation_results)
@app.route("/api/v1.0/stations")
def list_of_stations():
    all_stations = session.query (Station.station).all()
    session.close()
    stations = list(np.ravel(all_stations))
    return jsonify(stations)
@app.route("/api/v1.0/tobs")
def active_station():
    most_active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()
    active_station = most_active_stations[0]
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= query_date).all()
    session.close()
    tobs_results = []
    for date, tobs in results:
        tobs_d = {}
        tobs_d["date"] = date
        tobs_d["tobs"] = tobs

        tobs_results.append(tobs_d)
    return jsonify(tobs_results)

@app.route("/api/v1.0/<start>")
def temp_start(start= None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    start_results = session.query(*sel).filter(Measurement.date >= start).all()
    session.close()
    temp_results = []
    for TMIN,TAVG,TMAX in start_results:
        temp_d = {}
        temp_d["TMIN"] = TMIN
        temp_d["TAVG"] = TAVG
        temp_d["TMAX"] = TMAX
        temp_results.append(temp_d)
    return jsonify(temp_results)

@app.route("/api/v1.0/<start>/<end>")
def temp_range(start= None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    start_results = session.query(*sel).filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()
    temp_results = []
    for TMIN,TAVG,TMAX in start_results:
        temp_d = {}
        temp_d["TMIN"] = TMIN
        temp_d["TAVG"] = TAVG
        temp_d["TMAX"] = TMAX
        temp_results.append(temp_d)
    return jsonify(temp_results)

if __name__ == '__main__':
    app.run(debug=True)  
