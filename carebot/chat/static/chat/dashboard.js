document.addEventListener('DOMContentLoaded', function() {
    var map = L.map('heatmap').setView([37.8, -96], 4);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    fetch('/api/geolocation-data/')
    .then(response => response.json())
    .then(data => {
        var heatLayerData = data.map(function(item) {
            return [item.latitude, item.longitude, 1];
        });
        L.heatLayer(heatLayerData, {radius: 25, blur: 15, maxZoom: 17}).addTo(map);
    })
    .catch(error => console.error('Error loading geolocation data:', error));

});

