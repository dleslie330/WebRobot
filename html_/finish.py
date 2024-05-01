html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Thank You</title>
    <style>
        /* Your existing CSS styles */
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
    <div>
        Thank you for driving the PicoBot. Please refresh the page to join the queue after about 30 seconds cooldown.
    </div>
    <button onclick="location.reload()">Refresh</button> <!-- Refresh button -->
</body>
</html>

"""