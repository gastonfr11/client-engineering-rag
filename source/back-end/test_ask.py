import requests

url = "http://127.0.0.1:8080/ask"
payload = {
    "question": "¿Qué es Watsonx.ai?",
    "k": 3
}
resp = requests.post(url, json=payload)
print(resp.status_code)
print(resp.json())
