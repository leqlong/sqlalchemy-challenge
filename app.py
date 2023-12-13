# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")  # Replace with your database path

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

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
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/(start date YYYY-MM-DD)<br/>"
        f"/api/v1.0/(start date YYYY-MM-DD)/(end date YYYY-MM-DD)<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    # Calculate the date one year from the last date in the database
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert query results to a dictionary using date as the key and prcp as the value
    precipitation_dict = {date: prcp for date, prcp in results}
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations"""
    results = session.query(Station.station).all()

    # Convert list of tuples into normal list
    stations_list = list(np.ravel(results))
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature observations (TOBS) for the last year of the most active station"""
    # Calculate the date one year from the last date in the database
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the last year of temperature observation data for the most active station
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= one_year_ago).all()

    # Convert list of tuples into normal list
    tobs_list = list(np.ravel(results))
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):
    """
    Return the min, max, and average temperatures from the given start date to the end of the dataset.
    """
    session = Session(engine)
    try:
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    except ValueError:
        session.close()
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    session.close()

    if not results:
        return jsonify({"error": "No data found for the provided start date."}), 404

    temps = list(np.ravel(results))
    return jsonify(temps=temps)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """
    Return the min, max, and average temperatures between the given start and end dates.
    """
    session = Session(engine)
    try:
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
        end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        session.close()
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

    if start_date > end_date:
        session.close()
        return jsonify({"error": "End date must be after the start date."}), 400

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()

    if not results:
        return jsonify({"error": "No data found for the provided date range."}), 404

    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run(debug=True)