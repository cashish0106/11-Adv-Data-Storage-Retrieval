import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#####Database connection
engine = create_engine("sqlite:///Resources/Hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Station_class = Base.classes.station
Measure_class = Base.classes.measurement

session = Session(engine)

app = Flask(__name__)

@app.route("/")
def welcome():
    """<h1>List all available api routes.</h1>"""
    return (
        f"<h3>Available Routes:</h3>"
        f"<h5>/api/v1.0/precipitation</h5>"
        f"<h5>/api/v1.0/stations</h5>"       
        f"<h5>/api/v1.0/tobs</h5>"
        f"<h5>/api/v1.0/StartDate or /api/v1.0/StartDate/EndDate</h5>"
        f"<h5>&nbsp&nbsp&nbsp&nbsp&nbspwhere StartDate and EndDate in format YYYY-MM-DD </h5>"
    )
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all station"""
    stations = session.query(Station_class).all()
    all_stations=[]
    for station in stations:
        stat_dict={}
        stat_dict["Station ID"]=station.station
        stat_dict["Name"]=station.name
        stat_dict["latitude"]=station.latitude
        stat_dict["longitude"]=station.longitude
        stat_dict["elevation"]=station.elevation
        all_stations.append(stat_dict)
    return jsonify(all_stations)

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of weather last year"""
    st_date = dt.datetime(2016,1,1)-dt.timedelta(days=1)
    end_date=dt.datetime(2016,12,31)
    measurements = session.query(Measure_class).filter(Measure_class.date >=st_date).filter(Measure_class.date<=end_date).all()
    all_measure=[]
    for measure in measurements:
        measure_dict={}
        measure_dict["Station ID"]=measure.station
        measure_dict[str(measure.date)]=measure.prcp
        all_measure.append(measure_dict)
    return jsonify(all_measure)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperature for previous years"""
    #st_date = dt.datetime(2015,12, 31)
    #end_date=dt.datetime(2016,12,31)
    #measurements = session.query(Measure_class).filter(Measure_class.date >=st_date).filter(Measure_class.date<=end_date).all()
    measurements = session.query(Measure_class).all()
    all_measure=[]
    for measure in measurements:
        measure_dict={}
        measure_dict["Station ID"]=measure.station
        measure_dict[str(measure.date)]=measure.tobs
        all_measure.append(measure_dict)
    return jsonify(all_measure)

@app.route('/api/v1.0/<st_dt>', defaults={'end_dt': None})
@app.route('/api/v1.0/<st_dt>/<end_dt>')
def range_analysis(st_dt,end_dt):
    """Return a json list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range."""
    sel = [func.min(Measure_class.tobs).label('TMIN'), 
       func.max(Measure_class.tobs).label('TMAX'), 
       func.avg(Measure_class.tobs).label('TAVG')]

    s_date = dt.datetime.strptime(st_dt , '%Y-%m-%d')-dt.timedelta(days=1)
    if(end_dt):
        e_date = dt.datetime.strptime(end_dt , '%Y-%m-%d')
        temp_average = session.query(*sel).filter(Measure_class.date >=s_date).filter(Measure_class.date<=e_date).all()
    else:
            temp_average = session.query(*sel).filter(Measure_class.date >=s_date).all()
    measure_dict={}
    measure_dict["TMIN"]=temp_average[0].TMIN
    measure_dict["TMAX"]=temp_average[0].TMAX
    measure_dict["TAVG"]=round(temp_average[0].TAVG,2)
    return jsonify(measure_dict)

if __name__ == '__main__':
    app.run(debug=True)