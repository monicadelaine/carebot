const express = require('express');
const app = express();
const PORT = 3000;

app.use(express.static('public')); 
app.get('/api/geolocation-data', (req, res) => {

    const data = [
        { lat: 37.7749, lng: -122.4194, intensity: 1 }, ];
    res.json(data);
});

app.listen(PORT, () => console.log(`Server running on port ${PORT}`));