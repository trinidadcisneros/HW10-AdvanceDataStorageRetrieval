# import Flask
from flask import Flask, jsonify
import numpy as np
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Create an app, being sure to pass __name__
app = Flask(__name__)

# Formula for calculating temperature
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
    Returns:
        TMIN, TAVE, and TMAX
    """
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()


routes = ["routes:", "/api/v1.0/precipitation", "/api/v1.0/stations", "/api/v1.0/tobs", "/api/v1.0/<start>", "/api/v1.0/<start>/<end>"]

# Define what to do when a user hits the index route
@app.route("/")
def home():
    return jsonify(routes)



# Define what to do when a user hits the index route
@app.route("/api/v1.0/precipitation")
def precipitation():
# Initialize lists to store values from the Measurement Table
    measurement_date = []
    measurement_prcp = []

    # Querry measurement table for the last 12 months (365 days)
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.desc()).filter(Measurement.date>='2016-08-23').all()

    # List comprehensions to extract values from tuple
    measurement_date = [result[0] for result in results]
    measurement_prcp = [result[1] for result in results]

    stations = session.query(Measurement.station).group_by(Measurement.station).all()
    stations = np.ravel(stations)
    stations = stations.tolist()

    prcp_dict = dict(zip(measurement_date, measurement_prcp))
    return jsonify(prcp_dict)


# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def station_func():

    return jsonify(session.query(Measurement.station).group_by(Measurement.station).all())


# * `/api/v1.0/tobs`
#   * query for the dates and temperature observations from a year from the last data point.
#   * Return a JSON list of Temperature Observations (tobs) for the previous year.
# * `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`

@app.route("/api/v1.0/tobs")
def tobs():
# Initialize lists to store values from the Measurement Table
    measurement_date = []
    measurement_tobs = []

    # Querry measurement table for the last 12 months (365 days)
    results = session.query(Measurement.date, Measurement.tobs).order_by(Measurement.date.desc()).filter(Measurement.date>='2016-08-23').all()

    # List comprehensions to extract values from tuple
    measurement_date = [result[0] for result in results]
    measurement_tobs = [result[1] for result in results]

    tobs_dict = dict(zip(measurement_date, measurement_tobs))


    return jsonify(tobs_dict)


# * `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`
#   * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#   * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
#   * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>")
def start_date(start):

    return jsonify(calc_temps(start, '20180101'))


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    
    return jsonify(calc_temps(start, end))

if __name__ == "__main__":
    app.run(debug=True)

