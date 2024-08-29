const busRoutes = {
    "101": [
        {lat: 37.77, lng: -122.41},
        {lat: 37.78, lng: -122.42},
        {lat: 37.79, lng: -122.43}
    ],
    "102": [
        {lat: 37.76, lng: -122.40},
        {lat: 37.77, lng: -122.41},
        {lat: 37.78, lng: -122.42}
    ],
    "103": [
        {lat: 37.75, lng: -122.39},
        {lat: 37.76, lng: -122.40},
        {lat: 37.77, lng: -122.41}
    ],
    "104": [
        {lat: 37.74, lng: -122.38},
        {lat: 37.75, lng: -122.39},
        {lat: 37.76, lng: -122.40}
    ]
};

document.getElementById("busForm").addEventListener("submit", function(event) {
    event.preventDefault();
    const busNumber = document.getElementById("busNo").value;
    const route = busRoutes[busNumber];
    
    if (!route) {
        alert("Bus route not found.");
        return;
    }

    const start = route[0];
    const end = route[route.length - 1];

    // Construct the Google Maps URL for directions
    const url = `https://www.google.com/maps/dir/?api=1&origin=${start.lat},${start.lng}&destination=${end.lat},${end.lng}&travelmode=driving`;

    document.getElementById("mapFrame").src = url;
});
