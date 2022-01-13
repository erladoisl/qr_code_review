import json


import requests

data = {'surname': 'Гаязов', 
        'name': 'Радик', 
        'patronymic': 'Равилович',
        'date_of_birth': '1990-06-06 00:00:00+04',
        'response_type':"Вакцинирован",
        "document_date":"2021-07-29T21:00:00.000Z",
        "expired_at":"2022-07-28T21:00:00.000Z",
        "document_number":"1000080214691021",
        "file_path":"2021/11/cd5d68b4a136ff4a03aa1b3af7be2520.pdf"}

file_name = 'data\qr.jpg'
with open(file_name, 'rb') as f:
        r = requests.get('http://localhost:8081/qrcode/v1/verify', files={file_name: f})
        print(r.status_code)
        print(r.json())