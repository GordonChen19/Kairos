from datetime import datetime
from dateutil import parser
import requests
import json
import pymongo

from dotenv import load_dotenv
import os

load_dotenv()

Mongo_DB_API = os.getenv('Mongo_DB_API')
LTA_API = os.getenv('LTA_API')


myclient = pymongo.MongoClient(Mongo_DB_API)
db = myclient["hacksg"]
collection = db["busstoplist"]

def name_to_code(busstop_name):
    myquery = { "busstop_name": busstop_name}
    busstop_code = collection.find(myquery)

    for x in busstop_code:
        return x["busstop_code"]

def estimated_arrivals(bus_stop_code, service_no):
    url = f"http://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2?BusStopCode={bus_stop_code}&ServiceNo={service_no}"
    payload = {}
    files={}
    headers = {'AccountKey': LTA_API}
    response = requests.request("GET", url, headers=headers, data=payload, files=files)

    parsed_data = json.loads(response.text)
    next_buses = []
    for service in parsed_data.get("Services", []):
        for key in ["NextBus", "NextBus2", "NextBus3"]:
            next_bus = service.get(key, {})
            estimated_arrival_time_str = next_bus.get("EstimatedArrival")
            if estimated_arrival_time_str:
                # Parse EstimatedArrival time string to datetime object
                estimated_arrival_time = parser.isoparse(estimated_arrival_time_str)

                # Get the current time
                current_time = datetime.now(estimated_arrival_time.tzinfo)

                # Calculate time difference
                time_difference = estimated_arrival_time - current_time

                # Print EstimatedArrival time and time difference
                print("Estimated Arrival ({}):".format(key), estimated_arrival_time)
                print("Time difference (minutes):", str(time_difference))
                print("---")
                next_buses.append(int(str(time_difference).split(":")[1])+int(str(time_difference).split(":")[0])*60)
    return next_buses
