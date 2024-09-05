from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

API_KEY = '5b3ce3597851110001cf624888e303b3c4494fe6abf301482b685b4d'
OR_SERVICE_URL = 'https://api.openrouteservice.org/v2/directions/driving-car/geojson'

# Coordinates for Rohini Sector 17 and Rohini Sector 7
coords = {
    'DTU': [28.684629, 77.208069],
    'NSUT': [28.609374, 77.034838]
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

if __name__ == '__main__':
    app.run(debug=True)
