
import googlemaps

from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('Google_API')

gmaps = googlemaps.Client(key=api_key)

def get_geocode(address):
    try:
        geocode_result = gmaps.geocode(address)
        return geocode_result
    except:
        return None

def get_address_name(geocode):
    address_name =  geocode['formatted_address']
    lng, lat = geocode['geometry']['location']['lng'], geocode['geometry']['location']['lat']
    return address_name, (lat, lng)



def get_nearby_bus_stops(location, radius=200):
    places_result = gmaps.places_nearby(location=location, radius=radius, type='transit_station')
    nearest_bus_stops = places_result.get('results', [])
    return nearest_bus_stops[0]

def calculate_distance(origin, destination):
    distance_result = gmaps.distance_matrix(origins=[origin], destinations=[destination])
    if distance_result['rows'][0]['elements'][0]['status'] == 'OK':
        distance = distance_result['rows'][0]['elements'][0]['distance']['value']  # distance in meters
        return distance
    else:
        return None
    

def map_api(start,end,transit_preference=None, transit_mode=None):
    directions_result = gmaps.directions(start,
                                     end,
                                     mode="transit",
                                    transit_routing_preference=transit_preference,
                                    transit_mode = transit_mode
                                    )


    route = [directions_result[0]["legs"][0]["start_address"],directions_result[0]["legs"][0]["end_address"]]

    i = 0
    while True:
        try:

            # data = {"travel_mode": directions_result[0]["legs"][0]["steps"][i]["travel_mode"]}
            # dict.update(data)
            if (directions_result[0]["legs"][0]["steps"][i]["travel_mode"]=="WALKING"):
                j = 0
                k = 0
                while True:
                    try:
                        k += int(directions_result[0]["legs"][0]["steps"][i]["steps"][j]["duration"]['text'].split(" ", 1)[0])
                        j += 1
                    except:
                        data = {"travel_mode": directions_result[0]["legs"][0]["steps"][i]["travel_mode"],"time":k}
                        route.append(data)
                        break
            else:
                data = {
                    "travel_mode": directions_result[0]["legs"][0]["steps"][i]["travel_mode"],
                    "duration":directions_result[0]["legs"][0]["steps"][i]["duration"],
                    "vehicle_name":directions_result[0]["legs"][0]["steps"][i]["transit_details"]["line"]["vehicle"]["name"],
                    "line_name":directions_result[0]["legs"][0]["steps"][i]["transit_details"]["line"]["name"],
                    "arrival_stop":directions_result[0]["legs"][0]["steps"][i]["transit_details"]["arrival_stop"]['name'],
                    "departure_stop":directions_result[0]["legs"][0]["steps"][i]["transit_details"]["departure_stop"]["name"],
                    "num_stop":directions_result[0]["legs"][0]["steps"][i]["transit_details"]["num_stops"]
                }
                route.append(data)
            i += 1
        except:
            break

    return route


# source_geocode = get_geocode('Bishan Sky Habitat')

# source_address, source_location = get_address_name(source_geocode[0])

# print(source_address, source_location)

# destination_geocode = get_geocode('NTU')

# destination_address, destination_location = get_address_name(destination_geocode[0])

# print(destination_address, destination_location)

# print(calculate_distance(source_location, destination_location))




# print(get_nearby_bus_stops(location, radius=500))




# # Look up an address with reverse geocoding
# reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))

# Request directions via public transit
# now = datetime.now()
# directions_result = gmaps.directions("Sydney Town Hall",
#                                      "Parramatta, NSW",
#                                      mode="transit",
#                                      departure_time=now)

# Validate an address with address validation
# addressvalidation_result =  gmaps.addressvalidation(['1600 Amphitheatre Pk'], 
#                                                     regionCode='US',
#                                                     locality='Mountain View', 
#                                                     enableUspsCass=True)
