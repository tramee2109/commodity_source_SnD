import requests

url = "https://silverinstitute.org/wp-content/uploads/2024/07/World-Silver-Survey-2024.pdf"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

r = requests.head(url, headers=headers, timeout=15)
print(f"Silver Institute Survey 2024 HEAD Status: {r.status_code}, Length: {r.headers.get('content-length')} bytes")
