import requests

# API URL
url = "https://jsonplaceholder.typicode.com/users" #it is a fake REST API endpoint used for learning and testing APIs. 

try:
    # Sending GET request
    response = requests.get(url, timeout=5)

    # Print status code
    print("Status Code:", response.status_code)

    # Check for HTTP errors
    response.raise_for_status()

    # Convert JSON response to Python object
    data = response.json()

    print("\nComplete Data:\n")
    print(data)

    print("\nFirst User Details:\n")
    print("Name :", data[0]["name"])
    print("Email:", data[0]["email"])
    print("City :", data[0]["address"]["city"])

except requests.exceptions.Timeout:
    print("Request timed out")

except requests.exceptions.HTTPError as e:
    print("HTTP Error:", e)

except requests.exceptions.JSONDecodeError:
    print("Response is not valid JSON")

except requests.exceptions.RequestException as e:
    print("Some error occurred:", e)