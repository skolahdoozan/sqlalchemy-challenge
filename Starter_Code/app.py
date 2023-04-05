# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, cast, Date
import datetime as dt
import pandas as pd

#################################################
# Database Setup
#################################################

# reflect an existing database into a new model
engine = create_engine('sqlite:///Resources/hawaii.sqlite')
# reflect the tables
Base = automap_base()
Base.prepare(autoload_with = engine)
Base.classes.keys()
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Required Data for Queries
# Calculating the most recent date in the database
the_most_recent_date_measurement_txt = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
the_most_recent_date_measurement = list(session.query(Measurement.date).order_by(Measurement.date.desc()).first())
the_most_recent_date_measurement_str = str(the_most_recent_date_measurement)[2:-2]
the_most_recent_date_measurement_date=dt.datetime.strptime(the_most_recent_date_measurement_str, '%Y-%m-%d').date()
last_year = the_most_recent_date_measurement_date - dt.timedelta(days = 365)

# Finding the most active station in the datebase
station_number_of_readings = session.query(Measurement.station, func.count(Measurement.tobs)).\
                group_by(Measurement.station).\
                order_by(func.count(Measurement.tobs).desc()).all()
station_number_of_readings_df = pd.DataFrame(station_number_of_readings, columns = ['station', 'count'])
the_most_active_station = station_number_of_readings_df.loc[station_number_of_readings_df['count'].idxmax()]
the_most_active_station = the_most_active_station['station']


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
# Start at the homepage.
# List all the available routes.
@app.route('/')
def welcome():
    return(
        f'Available Routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/<br/')

# Retrieve only the last 12 months of data
@app.route('/api/v1.0/precipitation')
def percipation():
    session = Session(engine)
    result = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year).all()
    session.close()
    last_year_precipitation = {date:prcp for date, prcp in result}
    return jsonify(last_year_precipitation)
    
# Return a JSON list of stations from the dataset.
@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    result = session.query(Station.station, Station.longitude, Station.latitude, Station.elevation).all()
    station_list = []
    for station in result:
        station_dict = {}
        station_dict['name'] = station['station']
        station_dict['longitude'] = station['longitude']
        station_dict['latitude'] = station['latitude']
        station_dict['elevation'] = station['elevation']
        station_list.append(station_dict)
    
    session.close()
    return jsonify(station_list)


# Return a JSON list of stations from the dataset.
@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    result = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.station == the_most_active_station).\
            filter(Measurement.date >= last_year).all()
    date_and_temperature_the_most_active_station = {date:prcp for date, prcp in result}
    session.close()
    
    return jsonify(date_and_temperature_the_most_active_station)

@app.route('/api/v1.0/')
# Return a JSON list of the minimum temperature, the average temperature, 
# and the maximum temperature for a specified start or start-end range.
def api_v1_0 ():
    return ('Please enter a date in the format of YYYY-MM-DD')

@app.route('/api/v1.0/<start>')
def api_start (start):
    session = Session(engine)
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    qry = session.query(func.max(Measurement.tobs).label('max_temp'), func.min(Measurement.tobs).label('min_temp'), func.avg(Measurement.tobs).label('avg_temp')).\
                    filter(Measurement.station == the_most_active_station).\
                    filter(Measurement.date >= start_date)
    res = qry.one()
    max_temp = res.max_temp
    min_temp = res.min_temp
    avg_temp = res.avg_temp
    tobs_information = {'max_temp': max_temp, 'min_temp': min_temp, 'avg_temp': avg_temp}

    session.close()
    return jsonify (tobs_information)

@app.route('/api/v1.0/<start>/<end>')
def api_start_end (start, end):
    session = Session(engine)
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
    qry = session.query(func.max(Measurement.tobs).label('max_temp'), func.min(Measurement.tobs).label('min_temp'), func.avg(Measurement.tobs).label('avg_temp')).\
                    filter(Measurement.station == the_most_active_station).\
                    filter(Measurement.date >= start_date).\
                    filter(Measurement.date <= end_date)
    res = qry.one()
    max_temp = res.max_temp
    min_temp = res.min_temp
    avg_temp = res.avg_temp
    tobs_information = {'max_temp': max_temp, 'min_temp': min_temp, 'avg_temp': avg_temp}

    session.close()
    return jsonify (tobs_information)

if __name__ == '__main__':
    app.run(debug = True)