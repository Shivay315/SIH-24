from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dtc_transport.db'  # Or your preferred database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# OpenRouteService API key and URL
API_KEY = '5b3ce3597851110001cf624888e303b3c4494fe6abf301482b685b4d'
OR_SERVICE_URL = 'https://api.openrouteservice.org/v2/directions/driving-car/geojson'

# SQLAlchemy Models

class Route(db.Model):
    __tablename__ = 'routes'
    id = db.Column(db.Integer, primary_key=True)
    route_number = db.Column(db.String(10), nullable=False)
    route_name = db.Column(db.String(50), nullable=False)
    start_point = db.Column(db.String(50), nullable=False)
    end_point = db.Column(db.String(50), nullable=False)
    distance = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    buses = db.relationship('Bus', backref='route', lazy=True)
    stops = db.relationship('Stop', backref='route', lazy=True)

class Stop(db.Model):
    __tablename__ = 'stops'
    id = db.Column(db.Integer, primary_key=True)
    stop_name = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)

class Bus(db.Model):
    __tablename__ = 'buses'
    id = db.Column(db.Integer, primary_key=True)
    bus_number = db.Column(db.String(10), nullable=False)
    bus_type = db.Column(db.String(20), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    drivers = db.relationship('Driver', backref='bus', lazy=True)

class Driver(db.Model):
    __tablename__ = 'drivers'
    id = db.Column(db.Integer, primary_key=True)
    driver_name = db.Column(db.String(50), nullable=False)
    license_number = db.Column(db.String(20), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    buses = db.relationship('Bus', backref='driver', lazy=True)
    
class CrewShift(db.Model):
    __tablename__ = 'crew_shifts'
    id = db.Column(db.Integer, primary_key=True)
    crew_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)
    shift_start = db.Column(db.Time, nullable=False)
    shift_end = db.Column(db.Time, nullable=False)
    driver = db.relationship('Driver', backref='crew_shifts')
    bus = db.relationship('Bus', backref='crew_shifts')

class CrewHandover(db.Model):
    __tablename__ = 'crew_handover'
    id = db.Column(db.Integer, primary_key=True)
    old_crew_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    new_crew_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)
    handover_time = db.Column(db.DateTime, nullable=False)
    old_crew = db.relationship('Driver', foreign_keys=[old_crew_id])
    new_crew = db.relationship('Driver', foreign_keys=[new_crew_id])
    bus = db.relationship('Bus', backref='crew_handovers')

class RestPeriod(db.Model):
    __tablename__ = 'rest_periods'
    id = db.Column(db.Integer, primary_key=True)
    crew_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    rest_start = db.Column(db.Time, nullable=False)
    rest_end = db.Column(db.Time, nullable=False)
    driver = db.relationship('Driver', backref='rest_periods')

# Initialize the database (run only once to create tables)
with app.app_context():
    db.create_all()

# Route Finding Functionality
coords = {
    'Shahbad Village': [28.5856, 77.0916],
    'Delhi Engineering College': [28.6083, 77.0345],
    'Rohini Sector 16 Crossing': [28.7333, 77.1143],
    'Shree Krishna Apartment': [28.7180, 77.1118]
}

@app.route('/')
def index():
    locations = list(coords.keys())
    return render_template('index.html', locations=locations)

@app.route('/find_route', methods=['POST'])
def find_route():
    start = request.form.get('start')
    goal = request.form.get('goal')

    if start not in coords or goal not in coords:
        return jsonify({"error": "Invalid start or goal location."})

    start_coords = coords[start]
    goal_coords = coords[goal]

    headers = {
        'Authorization': API_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    payload = {
        'coordinates': [start_coords[::-1], goal_coords[::-1]]  # GeoJSON expects [lon, lat]
    }

    try:
        response = requests.post(OR_SERVICE_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        route_coords = data['features'][0]['geometry']['coordinates']
        route_coords = [[point[1], point[0]] for point in route_coords]  # Convert to [lat, lon]

        return jsonify({"route": route_coords})

    except requests.exceptions.HTTPError as http_err:
        return jsonify({"error": f"HTTP error occurred: {http_err}"})
    except Exception as err:
        return jsonify({"error": f"Other error occurred: {err}"})

# Linked Duty Scheduling Routes
@app.route('/assign_crew', methods=['POST'])
def assign_crew():
    crew_id = request.form.get('crew_id')
    bus_id = request.form.get('bus_id')
    shift_start = request.form.get('shift_start')
    shift_end = request.form.get('shift_end')

    shift = CrewShift(crew_id=crew_id, bus_id=bus_id, shift_start=shift_start, shift_end=shift_end)
    db.session.add(shift)
    db.session.commit()

    return jsonify({"message": "Crew assigned successfully."})

@app.route('/view_assignments', methods=['GET'])
def view_assignments():
    assignments = CrewShift.query.all()
    return jsonify([{'id': a.id, 'crew_id': a.crew_id, 'bus_id': a.bus_id, 'shift_start': a.shift_start, 'shift_end': a.shift_end} for a in assignments])

# Unlinked Duty Scheduling Routes
@app.route('/handover_bus', methods=['POST'])
def handover_bus():
    old_crew_id = request.form.get('old_crew_id')
    new_crew_id = request.form.get('new_crew_id')
    bus_id = request.form.get('bus_id')
    handover_time = request.form.get('handover_time')

    handover = CrewHandover(old_crew_id=old_crew_id, new_crew_id=new_crew_id, bus_id=bus_id, handover_time=handover_time)
    db.session.add(handover)
    db.session.commit()

    return jsonify({"message": "Bus handed over successfully."})

@app.route('/manage_rest', methods=['POST'])
def manage_rest():
    crew_id = request.form.get('crew_id')
    rest_start = request.form.get('rest_start')
    rest_end = request.form.get('rest_end')

    rest = RestPeriod(crew_id=crew_id, rest_start=rest_start, rest_end=rest_end)
    db.session.add(rest)
    db.session.commit()

    return jsonify({"message": "Rest period recorded successfully."})

if __name__ == '__main__':
    app.run(debug=True)
