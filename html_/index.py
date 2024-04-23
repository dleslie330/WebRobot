
html = """<!DOCTYPE html>
<html>
<head>
    <title>Web Robot</title>
    <style>
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
        #stop {
            top: 240px;
            right: 240px
        }
    </style>
    <script>
        function sendButton(buttonId) {
            var xhr = new XMLHttpRequest();
            xhr.open("GET", "/" + buttonId, true);
            xhr.send();
        }
    </script>
</head>
<body>
    <h1>Web Robot</h1>
    <p>Press the buttons to control the Picobot</p>
    <button id="quit" class="button" onclick="sendButton('quit')">Quit</button><br>
    <div class="container">
        <button id="forward" class="button" onclick="sendButton('forward')">Forward</button><br>
        <button id="left" class="button" onclick="sendButton('left')">Left</button>
        <button id="right" class="button" onclick="sendButton('right')">Right</button><br>
        <button id="back" class="button" onclick="sendButton('back')">Back</button><br>
        <button id="stop" class="button" onclick="sendButton('stop')">Stop</button><br>
    </div>
</body>
</html>
"""