html = """
<!DOCTYPE html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wait Page</title>
    <style>
        #wait-text {
            font-size: 36px; /* Adjust the font size as needed */
        }
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 20vh; /* Adjust the vertical margin as needed */
            font-size: 36px; /* Adjust the font size as needed */
        }
        button {
            margin-top: 20px; /* Adjust the top margin for the button */
            padding: 10px 20px; /* Adjust padding as needed */
            font-size: 24px; /* Adjust font size as needed */
            background-color: #008CBA; /* Button background color */
            color: white; /* Text color */
            border: none; /* Remove border */
            border-radius: 5px; /* Add border radius */
            cursor: pointer; /* Add cursor pointer */
        }
        button:hover {
            background-color: #005f7f; /* Darker background color on hover */
        }
    </style>
</head>
<body>
    <div id="wait-text">
        Please wait for <span id="time-placeholder">{time}</span> seconds for your turn.
    </div>
    <button onclick="location.reload()">Refresh <span id="refresh"></span></button> <!-- Refresh button -->

    <script>

        var reloaded = true;
        
        setTimeout(function() {
            if (!reloaded) {
                location.reload();
            }
        }, 0);

        // Function to update the time placeholder
        function updateTime(time) {
            document.getElementById('time-placeholder').innerText = time;
            if (time <= 0) {
                reloaded = false;
                // setTimeout(switchPage, 1000, '/ReadyToEnd');
                switchPage('/ReadyToPlay');   
            }
        }
        // Function to fetch time from the server
        function fetchTime() {
            fetch('/time')  // Assuming the server endpoint is '/time'
                .then(response => response.json())
                .then(data => {
                    updateTime(data.time);  // Assuming the response contains a 'time' field
                })
                .catch(error => console.error('Error fetching time:', error));
        }
        // Call fetchTime() initially and then every 1 second
        fetchTime();
        setInterval(fetchTime, 1000); 

        function updateRefresh(refresh){
            document.getElementById('refresh').innerText = refresh;
        }

        // Function to see if page needs to be reloaded
        function fetchReload() {
            fetch('/reload')  
                .then(response => response.json())
                .then(data => {
                    updateRefresh(data.status);
                })
                .catch(error => console.error('Error asking server to reload:', error));
        }
        // Call fetchReload() initially and then every 1 second
        fetchReload();
        setInterval(fetchReload, 1000); 

        setInterval(handleMessage, 1000);

        // Function to handle switching the webpage
        function switchPage(htmlFileName) {
            fetch(htmlFileName)
                .then(response => {
                    if (response.ok) {
                        return response.text(); // Get the HTML content as text
                    } else {
                        throw new Error('Failed to load page: ' + response.statusText);
                    }
                })
                .then(html => {
                    if (html.trim().toLowerCase() === 'not ready') {
                        console.log('Server is not ready to switch.');
                        // Do nothing
                    } else {
                        // Update the current page's content with the new HTML
                        document.open();
                        document.close();
                        document.write(html);
                    }
                })
                .catch(error => console.error('Error switching page:', error));
        }
    </script>
</body>
</html>
"""
