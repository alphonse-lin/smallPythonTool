import requests
path=r'C:\Users\CAUPD-BJ141\Desktop\002.png'
r = requests.post(
    "https://api.deepai.org/api/colorizer",
    files={
        'image': open(path, 'rb'),
    },
    headers={'api-key': 'quickstart-QUdJIGlzIGNvbWluZy4uLi4K'}
)
print(r.json())