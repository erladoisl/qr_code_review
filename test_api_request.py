import requests
url = 'http://localhost:8080'
# url = 'https://kipariss.gbubdd.ru'

file_name = 'data\qr.jpg'

with open(file_name, 'rb') as f:
        r = requests.get(f'{url}/api/qrservice')#, files={file_name: f})
        print(r.status_code)
        print(r.json())