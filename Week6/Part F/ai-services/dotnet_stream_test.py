import requests

url = "http://127.0.0.1:5194/api/Assistant/ask/stream"

payload = {
    "question": "Which book is about data structures and algorithms?"
}

with requests.post(
    url,
    json=payload,
    stream=True
) as response:

    print("Status:", response.status_code)

    for line in response.iter_lines(
        decode_unicode=True
    ):
        if line:
            print(line)