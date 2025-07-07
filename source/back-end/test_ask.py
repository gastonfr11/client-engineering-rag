import requests

resp = requests.post(
    "http://localhost:8080/ask",
    json={"question": "What is Watsonx.ai?", "k": 3}
)
print(resp.status_code)
print(resp.json())
