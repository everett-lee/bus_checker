from decouple import config
import requests
import json

tfl_auth_key = config('tfl_auth_key')
head = {'Authorisation': tfl_auth_key}

def get_bus(bus):
    matched_places = []
    bus = str(bus)
    data = {}
    url = 'https://api.tfl.gov.uk/Line/' + bus + '/Status'
    response = requests.get(url, headers=head)

    if response.status_code == 404:
        data = {'response_code': 404}
    elif response.status_code == 200:
        bus_info = json.loads(response.text)[0]
        if bus_info['lineStatuses']:
            iterate_over_statuses(bus_info['lineStatuses'], matched_places, data, bus)

    return data


def iterate_over_statuses(status_array, places_array, data, bus):
     count = 0
     for status in status_array:
        data[count] = {}
        data[count]['status_severity'] = status['statusSeverityDescription']

        if data[count]['status_severity']  == 'Good Service':
            pass

        else:
            data[count]['reason'] = status['reason']
            data[count]['location'] = []
            s = status['reason'].split(' ')
            places = []

            # creates list of possible place pairs
            for x, y in zip(s, s[1:]):
                places.append(x + ' ' + y)

            # gets a list of bus stops on relevant route
            url = 'https://api.tfl.gov.uk/line/' + bus + '/stoppoints'
            response = requests.get(url, headers=head)
            bus_stops = json.loads(response.text)

            # checks bus route for matches and adds list of unique results
            places_array += list(set([item['commonName'] for item in bus_stops if item['commonName'] in places]))
            # appends first words of status response
            places_array.append(' '.join(s[0:2]))

            # checks for disruption locations
            data[count]['latlon'] = []

            iterate_over_places(places_array, data, count)
            
        count += 1

def iterate_over_places(places_array, data, count):
    for place in places_array:
        response = requests.get('https://api.tfl.gov.uk/StopPoint/Search/' + place, headers=head)

        if response.status_code == 200:
            stop = json.loads(response.text)
            if stop['total'] != 0:
                lat = stop['matches'][0]['lat']
                lon = stop['matches'][0]['lon']
                if [lat, lon] not in data[count]['latlon']:
                    data[count]['latlon'].append([lat, lon])
