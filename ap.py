import numpy as np
from datetime import datetime, timedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Get first and last date of Measurement database
session = Session(engine)
last_date_query = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
last_date = datetime.strptime(last_date_query[0], '%Y-%m-%d')
first_date_query = session.query(Measurement.date).order_by(Measurement.date).first()
first_date = datetime.strptime(first_date_query[0], '%Y-%m-%d')
session.close()

app = Flask(__name__)

#Routes
@app.route("/")
def welcome():
    return (
        f"<h1>Welcome to the Climate API!</h1>"
        f"Data begins {first_date:%Y-%m-%d}<br/>"
        f"Data ends {last_date:%Y-%m-%d}"

        f"<h2>Available Routes:</h2>"

        f"<h3>Precipitation</h3>"
        f"<ul><li><a href = '/api/v1.0/precipitation' target='_blank'> /api/v1.0/precipitation </a><br/>" 
        f"returns date and prcp levels for each station in database for all dates</li>"
        f"<li><a href = '/api/v1.0/dailyprecipitation' target='_blank'>/api/v1.0/dailyprecipitation </a><br/>"
        f"returns date and average daily prcp levels collected in all stations for all dates in database</ul>"

        f"<h3>Stations</h3>"
        f"<ul><li><a href = '/api/v1.0/stations' target='_blank'>/api/v1.0/stations</a><br/>"
        f"returns list of station from the dataset</li></ul>"

        f"<h3>Temperature Observations </h3>"
        f"<h4>Temperature in the last year</h4>"
        f"Temperature observations from a year from the last data point <br/>"
        f"Currently 2017-08-23 to 2017-8-23<br/>"
        f"<ul><li> <a href = '/api/v1.0/tobs' target='_blank'> /api/v1.0/tobs </a><br/>"
        f"returns a list of the temperature, without details."
        f"<li> <a href = '/api/v1.0/tobsdetail' target='_blank'> /api/v1.0/tobsdetail </a><br/>"
        f"returns the temperatures with date and station.</ul>"

        f"<h4>Date Search - Temperature </h4>"
        f"The minimum temperature, the average temperature, and the max temperature for a given start or start-end range. <br/>"
        f"Following date formats should be YYYY-MM-DD <br/>"
        
        f"<h5>Summary - Returns summary values for date range </h5>"
        f"<ul><li>/api/v1.0/summary/start_date<br/>"
        f"(search date to end of last date, which is 2017-8-23)</br>"
        f"Example: <a href = '/api/v1.0/summary/2010-04-08' target='_blank'> /api/v1.0/summary/2010-04-08 </a></li>"
        f"<li>/api/v1.0/start_date/summary/start_date/end_date <br/>"
        f"Example: <a href = '/api/v1.0/summary/2010-04-08/2010-04-10' target='_blank'> /api/v1.0/summary/2010-04-08/2010-04-10 </a></li></ul>"

        f"<h5>Daily - Returns values for each day </h5>"
        f"<ul><li>/api/v1.0/daily/start_date<br/>"
        f"(search date to end of last date, which is 2017-8-23)</br>"
        f"Example: <a href = '/api/v1.0/daily/2010-04-08' target='_blank'> /api/v1.0/daily/2010-04-08 </a></li>"
        f"<li>/api/v1.0/start_date/daily/start_date/end_date <br/>"
        f"Example: <a href = '/api/v1.0/daily/2010-04-08/2010-04-10' target='_blank'> /api/v1.0/daily/2010-04-08/2010-04-10 </a></li></ul>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.station, Measurement.prcp).order_by(Measurement.date).all()
    session.close()

    all_prcp = []
    for date, station, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["station"] = station
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

@app.route("/api/v1.0/dailyprecipitation")
def dailyprecipitation():
    sel = [Measurement.date, func.avg(Measurement.prcp)]

    session = Session(engine)
    results = session.query(*sel).group_by(Measurement.date).all()
    session.close()

    daily_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["average_prcp"] = [prcp]
        daily_prcp.append(prcp_dict)

    return jsonify(daily_prcp)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()

    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    #calculate query date - within one year of last_date of data
    query_date = datetime(last_date.year - 1, last_date.month, last_date.day)

    #to include the end points, use "day-1"
    query_date = query_date - timedelta(days=1)

    results = session.query(Measurement.tobs).filter(Measurement.date > query_date).order_by(Measurement.date).all()
    session.close()

    lastyear_tobs = list(np.ravel(results))
    return jsonify(lastyear_tobs)

@app.route("/api/v1.0/tobsdetail")
def tobsdetail():
    #calculate query date - within one year of last_date of data
    query_date = datetime(last_date.year - 1, last_date.month, last_date.day)

    #to include the end points, use "day-1"
    query_date = query_date - timedelta(days=1)

    results = session.query(Measurement.date, Measurement.station, Measurement.tobs).filter(Measurement.date > query_date).order_by(Measurement.date).all()
    session.close()

    lastyear_tobs = []
    for date, station, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_dict["station"] = station
        lastyear_tobs.append(tobs_dict)

    return jsonify(lastyear_tobs)

@app.route("/api/v1.0/summary/<start>")
def date_search_start(start):
    sel = [func.min(Measurement.tobs), 
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)]
    
    fromDate = datetime.strptime(start, '%Y-%m-%d')

    #to include the end points, use "day-1"
    fromDate = fromDate - timedelta(days=1)
    
    # need "check_first_date" to allow search of 2010-01-01
    check_first_date = first_date - timedelta(days=1)

    #check search queries will work
    if check_first_date <= fromDate <= last_date:
        session = Session(engine)
        results = session.query(*sel).filter(Measurement.date >= fromDate).all()
        session.close()
        
        list_results = list(np.ravel(results))
        temp_dict = {}
        temp_dict["TMIN"] = list_results[0]
        temp_dict["TAVG"] = list_results[1]
        temp_dict["TMAX"] = list_results[2]
        return jsonify(temp_dict)
    else:
        return(
            f"<h5>Error: Please make sure your query dates are within database date range.</h5>"
            f"data begins {first_date:%Y-%m-%d}<br/>"
            f"data ends {last_date:%Y-%m-%d}")

@app.route("/api/v1.0/summary/<start>/<end>")
def date_search_startend (start, end):
    sel = [func.min(Measurement.tobs), 
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)]
    
    fromDate = datetime.strptime(start, '%Y-%m-%d')
    toDate = datetime.strptime(end, '%Y-%m-%d')

    #to include the end points, use "day-1"; not necessary for toDate
    fromDate = fromDate - timedelta(days=1)

    # need "check_first_date" to allow search of 2010-01-01
    check_first_date = first_date - timedelta(days=1)

    if check_first_date <= fromDate < toDate <= last_date:
        session = Session(engine)
        results = session.query(*sel).filter(Measurement.date >= fromDate).filter(Measurement.date <= toDate).all()
        session.close()
        
        list_results = list(np.ravel(results))
        temp_dict = {}
        temp_dict["TMIN"] = list_results[0]
        temp_dict["TAVG"] = list_results[1]
        temp_dict["TMAX"] = list_results[2]
        return jsonify(temp_dict)
    else:
        return(
            f"<h5> Error: Please check your query to make sure the start date is after end date.<br/> "
            f"Error: Please make sure your query dates are within database date range.</h5>"
            f"data begins {first_date:%Y-%m-%d}<br/>"
            f"data ends {last_date:%Y-%m-%d}")

@app.route("/api/v1.0/daily/<start>")
def date_search_dailystart(start):
    sel = [Measurement.date, 
        func.min(Measurement.tobs), 
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)]

    fromDate = datetime.strptime(start, '%Y-%m-%d')

    #to include the end points, use "day-1"
    fromDate = fromDate - timedelta(days=1)

    # need "check_first_date" to allow search of 2010-01-01
    check_first_date = first_date - timedelta(days=1)
    if check_first_date <= fromDate <= last_date:
        session = Session(engine)
        results = session.query(*sel).filter(Measurement.date >= fromDate).group_by(Measurement.date).all()
        session.close()

        all_dates = []
        for date, min, avg, max in results:
            temp_dict = {}
            temp_dict["date"] = date
            temp_dict["min"] = min
            temp_dict["avg"] = avg
            temp_dict["max"] = max
            all_dates.append(temp_dict)
        return jsonify(all_dates)
    else:
        return(
            f"<h5>Error: Please make sure your query dates are within database date range.</h5>"
            f"data begins {first_date:%Y-%m-%d}<br/>"
            f"data ends {last_date:%Y-%m-%d}")

@app.route("/api/v1.0/daily/<start>/<end>")
def date_search_dailystartend (start, end):
    sel = [Measurement.date, 
        func.min(Measurement.tobs), 
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)]
    
    fromDate = datetime.strptime(start, '%Y-%m-%d')
    toDate = datetime.strptime(end, '%Y-%m-%d')

    #to include the end points, use "day-1"
    fromDate = fromDate - timedelta(days=1)

    # need "check_first_date" to allow search of 2010-01-01
    check_first_date = first_date - timedelta(days=1)

    if check_first_date <= fromDate < toDate <= last_date:
        session = Session(engine)
        results = session.query(*sel).filter(Measurement.date >= fromDate).group_by(Measurement.date).filter(Measurement.date <= toDate).all()
        session.close()
        
        all_dates = []
        for date, min, avg, max in results:
            temp_dict = {}
            temp_dict["date"] = date
            temp_dict["min"] = min
            temp_dict["avg"] = avg
            temp_dict["max"] = max
            all_dates.append(temp_dict)
        return jsonify(all_dates)
    else:
        return(
            f"<h5> Error: Please check your query to make sure the start date is after end date.<br/> "
            f"Error: Please make sure your query dates are within database date range.</h5>"
            f"data begins {first_date:%Y-%m-%d}<br/>"
            f"data ends {last_date:%Y-%m-%d}")

if __name__ == '__main__':
    app.run(debug=True)