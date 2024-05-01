
html = """
<!DOCTYPE html>
<html>
<head>
    <title>Web Robot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 0vh; /* Adjust the vertical margin as needed */
            font-size: 36px; /* Adjust the font size as needed */
            user-select: none;
        }
        .container {
            width: 600px;
            height: 600px;
            border: 2px solid #000000;
            border-radius: 50%;
            position: relative;
            margin: 100px auto;
            background: #777777;
        }
        .button {
            width: 120px;
            height: 120px;
            background: #8d0bf8;
            position: absolute;
            border: none;
            outline: none;
            border-radius: 50%;
            color: white;
            font-size: 24px;
            pointer-events: auto;
        }
        #forward {
            top: 0;
            left: 240px;
        }
        #left, #right {
            top: 240px;
        }
        #left {
            left: 0;
        }
        #right {
            right: 0;
        }
        #back {
            bottom: 0;
            left: 240px;
        }
        #quit {
            bottom: 240px;
            right: 0;
            top: 0;
        }
        #disconnect {
            top: 240px;
            right: 240px;
        }
        #wait-text {
            position: absolute;
            top: 400px;
            left: 5;
            font-size: 24px;
            color: black;
        }
    </style>
</head>
<body>
    <h1>Web Robot</h1>
    <h2>Press the buttons to control the Picobot</p>
    <div id="wait-text">
        You have <span id="time-placeholder">{time}</span> seconds to complete the maze!
    </div>
    <button id="quit" class="button">Quit</button><br>
    <div class="container">
        <button id="forward" class="button">Forward</button><br>
        <button id="left" class="button">Left</button>
        <button id="right" class="button">Right</button><br>
        <button id="back" class="button">Back</button><br>
        <button id="disconnect" class="button">Disconnect</button><br>
    </div>
    <img id="videoPlayer" autoplay></img>
    <script>
        var buttonDown = false;
        var buttonID = "";

        const videoPlayer = document.getElementById('videoPlayer');

        // Function to fetch and display the MJPEG video stream
        function playVideo() {
            fetch('/video_stream')  // Request MJPEG video stream from server
                .then(response => {
                    const reader = response.body.getReader(); // Get the response body reader

                    // Function to read and display MJPEG frames
                    function readStream({ done, value }) {
                        if (done) {
                            console.log('Stream ended');
                            return;
                        }

                        console.log('Received chunk:', value);

                        // Convert received data to base64
                        const base64String = btoa(String.fromCharCode.apply(null, new Uint8Array(value)));

                        // Update the image source with the new JPEG data
                        videoPlayer.src = `data:image/jpeg;base64,${base64String}`;
                    }

                })
                .catch(error => console.error('Error fetching video stream:', error));

        }

        setInterval(playVideo, 100);

        function sendButton(buttonId) {
            // If the button pressed is "disconnect", request an HTML page from the server
            if (buttonId === "disconnect") {
                switchPage("/disconnect");
            } else {
                var xhr = new XMLHttpRequest();
                xhr.open("GET", "/" + buttonId, true);
                xhr.send();
            }
        }

        document.getElementById("forward").addEventListener("mousedown", function() {
            buttonDown = true;
            buttonID = "forward";
        });

        document.getElementById("right").addEventListener("mousedown", function() {
            buttonDown = true;
            buttonID = "right";
        });

        document.getElementById("back").addEventListener("mousedown", function() {
            buttonDown = true;
            buttonID = "back";
        });

        document.getElementById("left").addEventListener("mousedown", function() {
            buttonDown = true;
            buttonID = "left";
        });

        document.getElementById("quit").addEventListener("mousedown", function() {
            buttonDown = true;
            buttonID = "quit";
        });

        document.getElementById("disconnect").addEventListener("mousedown", function() {
            buttonDown = true;
            buttonID = "disconnect";
        });

        document.getElementById("forward").addEventListener("mouseup", function() {
            buttonDown = true;
            buttonID = "stop";
        });

        document.getElementById("right").addEventListener("mouseup", function() {
            buttonDown = true;
            buttonID = "stop";
        });

        document.getElementById("back").addEventListener("mouseup", function() {
            buttonDown = true;
            buttonID = "stop";
        });

        document.getElementById("left").addEventListener("mouseup", function() {
            buttonDown = true;
            buttonID = "stop";
        });

        document.getElementById("quit").addEventListener("mouseup", function() {
            buttonDown = true;
            buttonID = "quit";
        });

        setInterval(function() {
            if (buttonDown) {
                buttonDown = false;
                sendButton(buttonID);
            }
        }, 10); 

        var reloaded = true;
        
        setTimeout(function() {
            if (!reloaded) {
                location.reload();
            }
        }, 0);

        // Function to fetch and play the video stream
        function playVideo() {
            fetch('/video_stream')  // Assuming the server endpoint is '/video_stream'
                .then(response => {
                    if (response.ok) {
                        return response.blob(); // Get the video stream as a Blob object
                    } else {
                        throw new Error('Failed to fetch video stream: ' + response.statusText);
                    }
                })
                .then(blob => {
                    // Convert the Blob object to a URL
                    const videoUrl = URL.createObjectURL(blob);
                    // Set the URL as the source of the <video> element
                    document.getElementById('videoPlayer').src = videoUrl;
                })
                .catch(error => console.error('Error fetching video stream:', error));
        }

        // Call playVideo() function to start playing the video
        setInterval(playVideo, 1000);

        // Function to update the time placeholder
        function updateTime(time) {
            document.getElementById('time-placeholder').innerText = time;
            if (time <= 0) {
                // setTimeout(switchPage, 1000, '/ReadyToEnd');
                switchPage('/ReadyToEnd');   
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
                        console.log('Server was not ready to switch you.');
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