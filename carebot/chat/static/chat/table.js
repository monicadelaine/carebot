document.addEventListener('DOMContentLoaded', function() {
    console.log('Requesting table data...');
    fetch('/api/table-data/')
    .then(response => response.json())
    .then(data => {
        console.log(data.table_data); 
        const tableBody = document.getElementById('resources-table').getElementsByTagName('tbody')[0];
        tableBody.innerHTML = ''; 

        if(data.table_data && data.table_data.length > 0) {
            data.table_data.sort((a, b) => b.request_count - a.request_count);

            data.table_data.forEach(item => {
                let row = tableBody.insertRow();
                
                let cellCounty = row.insertCell(0);
                cellCounty.textContent = item.county;
                
                let cellRequests = row.insertCell(1);
                cellRequests.textContent = item.request_count;
            });
        } else {
            console.log('No table data available');
        }
    })
    .catch(error => console.error('Error loading table data:', error));
});