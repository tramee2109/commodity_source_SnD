import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

urls = [
    "https://icsg.org/wp-content/uploads/Table1.pdf",
    "https://icsg.org/wp-content/uploads/Table2.pdf",
    "https://icsg.org/wp-content/uploads/Chart1.pdf"
]

for u in urls:
    r = requests.head(u, headers=headers, timeout=15)
    print(f"ICSG: {u.split('/')[-1]} -> Status {r.status_code}, Length: {r.headers.get('content-length')} bytes")
