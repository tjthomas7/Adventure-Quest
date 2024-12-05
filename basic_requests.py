# One-time import of requests library
import requests


# Get data from a URL
response = requests.get("https://httpbin.org/base64/SGVsbG8gV29ybGQh")


# Print out the content of the response
print(response.text)