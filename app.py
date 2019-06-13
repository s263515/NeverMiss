from flask import Flask, jsonify, abort, request, Response, render_template
from flask_cors import CORS
import db_interaction
import location

app = Flask(__name__)
CORS(app, methods=["GET", "POST", "PUT", "DELETE"])
global forward
forward = True

# Format the data into proper form for HTTP reply
def prepare_for_json_stops(item):
    """
    Convert the stop information in a dictionary for easing the JSON creation
    """
    stop = dict()
    stop['name'] = item[0]
    stop['latitude'] = item[1]
    stop['longitude'] = item[2]
    return stop


def prepare_for_json_pass_info(item):
    """
    Convert the pass_info in a dictionary for easing the JSON creation
    """
    pass_info = dict()
    pass_info['ID'] = item[0]
    pass_info['destination'] = item[1]
    pass_info['profile_photo_address'] = item[2]
    pass_info['region'] = item[3]
    return pass_info


def updateLocationInfo(forward, coordinate):
    db_interaction.update_next_station(location.reason_next_station(forward, coordinate[0], coordinate[1]),coordinate[0], coordinate[1])
    db_interaction.update_current_station(location.reason_current_station(forward, coordinate[0], coordinate[1]),coordinate[0], coordinate[1])
    print("Data updated")
    print("current station: "+location.reason_current_station(forward, coordinate[0], coordinate[1]))
    print("next station: "+location.reason_next_station(forward, coordinate[0], coordinate[1]))



# add information about the destination of the passengers, later can used to display the message

# ---------- REST SERVER ----------
@app.route('/api/v1.0/stops', methods=['GET'])
def get_stops():
    stops = []
    station_list = db_interaction.get_stops()
    for item in station_list:
        stop = prepare_for_json_stops(item)
        stops.append(stop)
    # This function is only made for mobile application
    return jsonify(stops)


@app.route('/api/v1.0/next_stop', methods=['GET'])
def get_next_station():
    item = db_interaction.get_next_station()
    next_stop_json = prepare_for_json_stops(item)
    return jsonify({'stops': next_stop_json})


@app.route('/api/v1.0/current_stop', methods=['GET'])
def get_current_stop():
    item = db_interaction.get_current_station()
    next_stop_json = prepare_for_json_stops(item)
    return jsonify({'stops': next_stop_json})


@app.route('/api/v1.0/pass_info', methods=['POST'])
def insert_pass_info():
    # get the request body
    add_info = request.json
    # check whether a passenger_info is present in the request or not
    if (add_info is not None) and ('ID' in add_info) and ('destination' in add_info) and (
            'profile_photo_address' in add_info) and ('region' in add_info):
        ID = add_info['ID']
        destination = add_info['destination']
        profile_photo_address = add_info['profile_photo_address']
        region = add_info['region']
        # insert in the database
        db_interaction.insert_pass_info(ID, destination, profile_photo_address, region)
        return Response(status=201)
    # return an error in case of problems
    abort(403)


@app.route('/api/v1.0/pass_info', methods=['GET'])
def get_pass_info():
    info_all = []
    item_list = db_interaction.get_all_pass_info()
    for item in item_list:
        info = prepare_for_json_pass_info(item)
        info_all.append(info)
    return jsonify({'info_all': info_all})


@app.route('/api/v1.0/pass_info/<int:pass_ID>', methods=['PUT'])
def update_pass_info(pass_ID):
    add_info = request.json
    if add_info is not None and ('destination' and 'profile_photo_address' and 'region') in add_info:
        destination = add_info['destination']
        profile_photo_address = add_info['profile_photo_address']
        region = add_info['region']
        db_interaction.util_insert_or_update_pass_info(int(pass_ID), destination, profile_photo_address, region)
        return Response(status=200)
    # return an error in case of problems
    abort(403)


@app.route('/api/v1.0/GPS_update', methods=['PUT'])
def update_location_info():
    add_info = request.json
    if (add_info is not None) and ('latitude' in add_info) and ('longitude' in add_info):
        latitude = float(add_info['latitude'])
        longitude = float(add_info['longitude'])
        print("current coordinate:")
        print(latitude,longitude)
        updateLocationInfo(forward, (latitude,longitude))
        return Response(status=200)
    # return an error in case of problems
    abort(403)

@app.route('/api/v1.0/passenger_needs_to_stop', methods=['GET'])
def get_passengers_needs_to_stop():
    current_stop = db_interaction.get_current_station()[0]
    if (current_stop == '__Not_Avaliable__'):
        next_stop = db_interaction.get_next_station()[0]
        passengers = db_interaction.get_pass_info_by_destination(next_stop)
    else:
        passengers = db_interaction.get_pass_info_by_destination(current_stop)
    region1 = 0
    region2 = 0
    for passenger in passengers:
        if passenger[3] == 1:
            region1 = region1 + 1
        if passenger[3] == 2:
            region2 = region2 + 1
    return jsonify({'region1':region1, 'region2':region2})

@app.route('/api/v1.0/bus_status', methods=['GET'])
def get_bus_status():
    if forward:
        return jsonify({'direction':"Tolmino"})
    else:
        return jsonify({'direction':"ADRIANO"})

@app.route('/api/v1.0/commands',methods=['PUT'])
def remote_commands():
    command = request.json
    global forward
    if (command is not None) and ('reset' and 'direction') in command:
        if command['reset'] == 1:
            print ("Reset passeger information!")
            db_interaction.delete_all_pass_info()
        if command['direction'] == 1:
            print ("Now moving towards Tolmino!")
            forward = True
        else:
            print ("Now moving towards ADRIANO")
            forward = False
        return Response(status=200)
    abort(403)


if __name__ == '__main__':
    app.run(host="0.0.0.0")
