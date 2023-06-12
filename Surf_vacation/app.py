# Import the dependencies.
import sqlalchemy
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import numpy as np
import datetime



#################################################
# Database Setup
#################################################


engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()

# Reflect the database tables
Base.prepare(engine, reflect=True)


# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station


# Create our session (link) from Python to the DB
session = Session(engine)



#################################################
# Flask Setup
#################################################
# Create Flask app
app = Flask(__name__)




#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """Homepage"""
    return (
        f"Welcome to the Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date (Enter start date in yyyy-mm-dd format)<br/>"
        f"/api/v1.0/start_date/end_date (Enter start and end dates in yyyy-mm-dd format)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Precipitation data"""
    
    # Query the precipitation data
    last_12_months = session.query(measurement.date, measurement.prcp) \
                    .filter(measurement.date >= '2016-08-23') \
                    .all()
    
    # Convert the result to a dictionary
    precipitation_data = {date: prcp for date, prcp in last_12_months}
    
    # Return the result as JSON response
    return jsonify(precipitation_data)


@app.route("/api/v1.0/stations")
def stations():
    """Station data"""
    
    # Query the station data
    station_data = session.query(station.station).all()
    
    # Convert the result to a list
    stations_list = [station[0] for station in station_data]
    
    # Return the result as JSON response
    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    """Temperature observations for the most active station in the previous year"""

    # Find the most active station
    most_active_station = session.query(measurement.station, func.count(measurement.tobs)) \
        .group_by(measurement.station) \
        .order_by(func.count(measurement.tobs).desc()) \
        .first()[0]

    # Calculate the date one year before the last date in the dataset
    last_date = session.query(func.max(measurement.date)).scalar()
    last_date = datetime.datetime.strptime(last_date, '%Y-%m-%d')
    one_year_ago = last_date - datetime.timedelta(days=365)

    # Query the temperature observations for the most active station within the date range of the previous year
    results = session.query(measurement.date, measurement.tobs) \
        .filter(measurement.station == most_active_station) \
        .filter(measurement.date >= one_year_ago.strftime('%Y-%m-%d')) \
        .all()

    # Create a list of temperature observations
    temperature_data = [{'Date': date, 'Temperature': temp} for date, temp in results]

    # Return the result as JSON response
    return jsonify(temperature_data)



@app.route("/api/v1.0/temperature/<start>")
@app.route("/api/v1.0/temperature/<start>/<end>")
def temperature_stats(start, end=None):
    """Temperature statistics for the specified date range"""

    # Query the temperature statistics based on the specified start and end dates (if provided)
    if end:
        results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)) \
            .filter(measurement.date >= start) \
            .filter(measurement.date <= end) \
            .all()
    else:
        results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)) \
            .filter(measurement.date >= start) \
            .all()

    # Create a dictionary to store the temperature statistics
    temperature_stats = {
        'Start Date': start,
        'End Date': end,
        'Min Temperature': results[0][0],
        'Avg Temperature': results[0][1],
        'Max Temperature': results[0][2]
    }

    # Return the result as JSON response
    return jsonify(temperature_stats)


    # Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
