import requests
import time

def update_GPS_coordinate(coordinate):
    payload = dict()
    payload['latitude']=coordinate[0]
    payload['longitude']=coordinate[1]
    resp = requests.put('http://localhost:5000/api/v1.0/GPS_update', json = payload)
    print(resp)

if __name__ == '__main__':
    filename = 'Linea56.txt'
    f = open(filename,'r')
    GPS_coordinates = f.readlines()
    for line in GPS_coordinates:
        coordinate = line[:-1].split(",")
        update_GPS_coordinate(coordinate)
        time.sleep(5)