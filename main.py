import requests

print ("start")
payload = {'file_id': 'Music/alterego.wav', 'start_offset_ms': 0}
r = requests.put("http://10.0.0.200:8080/api/current-song", json=payload)
print ("sent")
print (r.status_code)

print (r.content)