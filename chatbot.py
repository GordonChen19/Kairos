from constants import start_message, walking, mrt, bus
from extractions_pipeline.extraction_chain import extraction_chain

from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('Telegram_API')

#To call extraction chain call extraction_chain(input)

import telebot
from telebot import types
import time
from database import POST, GET, DELETE, GET_PARTICULAR

from maps_api import map_api, get_geocode, get_address_name, calculate_distance


user_data = {}
tmp_route_store = {}
selected_route = {}

tb = telebot.TeleBot(API_KEY)


def get_route_message(route):
    source = route[0]
    destination = route[1]


    route_message = source 
    route_message += "\n"
    index = 2
    while index < len(route):
        travel = route[index]
        if travel['travel_mode'] == 'WALKING':
            tmp = walking.format(approx_walking_time= str(travel['time']))
            route_message += tmp
            route_message += "\n"
        elif travel['travel_mode'] == 'TRANSIT':

            route_message += f"{travel['departure_stop']}"
            route_message += "\n"
            if travel['vehicle_name'] == 'Bus':
                tmp = bus.format(approx_bus_time = travel['duration']['text'], bus_number = travel['line_name'])
                route_message += tmp
                route_message += "\n"
            elif travel['vehicle_name'] == 'Subway':
                tmp = mrt.format(approx_train_time = travel['duration']['text'], line_name=travel['line_name'])
                route_message += tmp
                route_message += "\n"
            route_message += f"{travel['arrival_stop']}"
            route_message += "\n"
        index+=1
    route_message += destination 
    return route_message


@tb.callback_query_handler(func=lambda call: call.data == 'save_route')
def save_route(call):
    global user_data
    chat_id = call.message.chat.id
    user_data[chat_id] = {}

    POST(chat_id, tmp_route_store[chat_id])
    tb.send_message(chat_id, "Route saved successfully")


@tb.callback_query_handler(func=lambda call: call.data.startswith("route_callback:"))
def delete_route_callback(call):
    global selected_route
    chat_id = call.message.chat.id

    route_id = call.data.split(":")[1]

    route = GET_PARTICULAR(route_id)[0]['data']
    
    tb.send_message(chat_id, "Turn off and on your live location to enable live route tracking.")

    selected_route[chat_id] = route




@tb.message_handler(func=lambda message: message.text == 'Select Routes')
def select_route(message):
    chat_id = message.chat.id
    
    saved_routes = GET(chat_id)


    if len(saved_routes) == 0:
        tb.send_message(chat_id, "No routes available. Please add a route first by clicking Modify Routes or typing it in the chat.")
    else:

         # Create a new inline keyboard
        route_callback = "route_callback"
        inline_keyboard = types.InlineKeyboardMarkup()
        for route in saved_routes:
            button = types.InlineKeyboardButton(route['data'][0] + ' -> ' + route['data'][1], callback_data=route_callback+':'+str(route['_id']))
            inline_keyboard.row(button)

        tb.send_message(chat_id, "Please select a Route:", reply_markup=inline_keyboard)




@tb.message_handler(func=lambda message: message.text == 'Modify Routes')
def modify_routes(message):
    chat_id = message.chat.id

    # Create a new inline keyboard
    add_route = "Add Route"
    delete_route = "Delete Route"

    inline_keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Add Route", callback_data=add_route)
    button2 = types.InlineKeyboardButton("Delete Route", callback_data=delete_route)
    inline_keyboard.row(button1, button2)

    tb.send_message(chat_id, "How would you like to modify your routes:", reply_markup=inline_keyboard)


@tb.message_handler(func=lambda message: message.text.startswith('/source'))
def less_walking_source(message):
    global tmp_route_store
    user_id = message.chat.id

    source_location = message.text[len('/source'):].strip()
    
    geocode_data = get_geocode(source_location)

    try:
        address_name, location = get_address_name(geocode_data[0])
        user_data[user_id]['source'] = address_name + ', Singapore'
    except:
        tb.send_message(user_id, "This is not a valid location. Please enter a valid location")


    if len(user_data[user_id]) == 3:
        tb.send_chat_action(user_id, 'typing')
        route = map_api(user_data[user_id]['source'], user_data[user_id]['destination'], None if user_data[user_id]['transit_preference'] == 'None' else user_data[user_id]['transit_preference'])

        tmp_route_store[user_id] = route
        inline_keyboard = types.InlineKeyboardMarkup()
        
        button = types.InlineKeyboardButton("Save", callback_data="save_route")
        inline_keyboard.row(button)

        tb.send_message(user_id, get_route_message(route), reply_markup=inline_keyboard)
        
        


@tb.message_handler(func=lambda message: message.text.startswith('/destination'))
def less_walking_destination(message):
    global tmp_route_store
    user_id = message.chat.id
    destination_location = message.text[len('/destination'):].strip()

    geocode_data = get_geocode(destination_location)

    try:
        address_name, location = get_address_name(geocode_data[0])
        user_data[user_id]['destination'] = address_name + ', Singapore'
    except:
        tb.send_message(user_id, "This is not a valid location. Please enter a valid location")

    print(user_data[user_id])
    if len(user_data[user_id]) == 3:
        tb.send_chat_action(user_id, 'typing')
        route = map_api(user_data[user_id]['source'], user_data[user_id]['destination'], None if user_data[user_id]['transit_preference'] == 'None' else user_data[user_id]['transit_preference'])
        tmp_route_store[user_id] = route
        inline_keyboard = types.InlineKeyboardMarkup()
        
        button = types.InlineKeyboardButton("Save", callback_data="save_route")
        inline_keyboard.row(button)

        tb.send_message(user_id, get_route_message(route), reply_markup=inline_keyboard)


@tb.callback_query_handler(func=lambda call: call.data == 'less_walking')
def less_walking(call):
    global user_data
    chat_id = call.message.chat.id
    user_data[chat_id] = {}
    
    tb.send_message(chat_id, "Select your source and destination by typing in /source followed by the location. For example, '/source Bishan Sky Habitat'")
    user_data[chat_id]['transit_preference'] = 'less_walking'


@tb.callback_query_handler(func=lambda call: call.data == 'fewer_transfers')
def fewer_transfers(call):
    global user_data
    chat_id = call.message.chat.id
    user_data[chat_id] = {}
    tb.send_message(chat_id, "Select your source and destination by typing in /source followed by the location. For example, '/source Bishan Sky Habitat'")
    user_data[chat_id]['transit_preference'] = 'fewer_transfers'


@tb.callback_query_handler(func=lambda call: call.data == 'default')
def default(call):
    global user_data
    chat_id = call.message.chat.id
    user_data[chat_id] = {}
    tb.send_message(chat_id, "Select your source and destination by typing in /source followed by the location. For example, '/source Bishan Sky Habitat'")
    user_data[chat_id]['transit_preference'] = 'None'

@tb.callback_query_handler(func=lambda call: call.data == 'custom')
def custom(call):
    chat_id = call.message.chat.id
    tb.send_message(chat_id, "Type how you go to work using MRT and BUS. E.g. I take the MRT from Bishan to Orchard, then BUS from Orchard to Suntec City")

@tb.callback_query_handler(func=lambda call: call.data == 'Add Route')
def add_route(call):
    global user_data
    chat_id = call.message.chat.id
    user_data[chat_id] = {}

    methods = {"Least walking":"less_walking",  "Fewest transfers":"fewer_transfers", "Shortest Route": "default", "Custom Route":"custom"}
    
    inline_keyboard = types.InlineKeyboardMarkup()
    for method, callback in methods.items():
        button = types.InlineKeyboardButton(method, callback_data=callback)
        inline_keyboard.row(button)

    tb.send_message(chat_id, "Select your preferred route", reply_markup=inline_keyboard)
    



#Boiler Plate Code
def display_routes(call,route_callback,initial_text):
    chat_id = call.message.chat.id
    
    saved_routes = GET(chat_id)

    if len(saved_routes) == 0:
        tb.send_message(chat_id, "No routes available.")
    else:

         # Create a new inline keyboard
        inline_keyboard = types.InlineKeyboardMarkup()
        for route in saved_routes:
            button = types.InlineKeyboardButton(route['data'][0] + ' -> ' + route['data'][1], callback_data=route_callback+':'+str(route['_id']))
            inline_keyboard.row(button)

        tb.send_message(chat_id, initial_text, reply_markup=inline_keyboard)


@tb.callback_query_handler(func=lambda call: call.data.startswith("delete_route_callback:"))
def delete_route_callback(call):
    chat_id = call.message.chat.id

    route_id = call.data.split(":")[1]
    DELETE(route_id)
    tb.send_message(chat_id, "Route deleted successfully")


@tb.callback_query_handler(func=lambda call: call.data == 'Delete Route')
def delete_route(call):
    global user_data
    chat_id = call.message.chat.id
    user_data[chat_id] = {}

    route_callback = "delete_route_callback"
    initial_text = "Please select a Route to delete"
    
    display_routes(call,route_callback,initial_text)

    
# Initialize and start the Telegram bot session
from bus_api import name_to_code, estimated_arrivals

@tb.message_handler(content_types=['location'])
def handle_location(message):
    # Get the chat ID of the user who sent the location
    chat_id = message.chat.id
    route = selected_route[chat_id]
    tb.send_message(chat_id, "Tracking you on your last selected route from " + route[0] + " to " + route[1] + "...")


    def send_notification(departure, bus_no, walking_time):
        station_code = name_to_code(departure)
        times = estimated_arrivals(station_code, bus_no)
        if walking_time > times[0]:
            tb.send_message(chat_id, f"To walk to {bus_no} takes approx {walking_time} minutes. The nextbus is arriving in {times[0]} minutes. It is likely you will miss the bus. The subsequent bus comes in another {times[1]} minutes and the one after that comes in {times[2]} minutes.")
        else:
            tb.send_message(chat_id, f"The next bus comes in {times[0]} minutes. Get ready to leave in {times[0]-walking_time}.")

  
    index = 2

    while True:
        try:
        # Get latitude and longitude from the location message
            latitude = message.location.latitude
            longitude = message.location.longitude
            if index == len(route) or index == (len(route)-1):
                break
            
            if route[index]['travel_mode'] == 'WALKING' and index + 1 < len(route) and route[index + 1]['travel_mode']=='TRANSIT':
                if route[index + 1]['vehicle_name'] == 'Bus':
                    send_notification(route[index+1]['departure_stop'],  route[index+1]['line_name'],route[index]['time'])
                while True:
                    latitude = message.location.latitude
                    longitude = message.location.longitude

                    geocode = get_geocode(route[index+1]['departure_stop'])
                    _, location = get_address_name(geocode[0])

                    if calculate_distance([latitude, longitude], location) < 100:
                        index += 1
                        break
                    time.sleep(20)
            else:
                while True:
                    latitude = message.location.latitude
                    longitude = message.location.longitude
                    geocode = get_geocode(route[index]['arrival_stop'])
                    _, location = get_address_name(geocode[0])

                    if calculate_distance([latitude, longitude], location) < 100:
                        index += 1
                        break  

        except:
            tb.send_message(chat_id, f"Please share your location")
            break
        time.sleep(20)

# Function to handle '/start' command
@tb.message_handler(commands=['start','new_chat_members'])
def start(message):
    global user_data
    chat_id = message.chat.id
    user_data[chat_id] = {}

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

    # Define the buttons
    button1 = types.KeyboardButton('Select Routes')
    button2 = types.KeyboardButton('Modify Routes')

    # Add the buttons to the keyboard
    markup.row(button1, button2)

    # Send the message with the keyboard
    tb.send_message(chat_id, start_message, reply_markup=markup)




@tb.message_handler(func=lambda message: True)
def handle_all_other_messages(message):
    global user_data, tmp_route_store
    chat_id = message.chat.id
    user_data[chat_id] = {}

    try:
        response = extraction_chain(message)['Transports']
        if len(response) == 0:
            tb.send_message(chat_id, "We can not convert your text to a route. Please try again.")
        else:
            journey = ""
            entire_journey = []
            for connect in response:
                route = map_api(start = connect['source'], end = connect['destination'], transit_mode = connect['transportationMode'].value)
                entire_journey.extend(route[2:])
                get_route_message(route)
                journey += get_route_message(route)
                journey += "\n"

            print(response)
            tmp_route_store[chat_id] = [response[0]['source']] + [response[-1]['destination']] + [entire_journey]
            inline_keyboard = types.InlineKeyboardMarkup()
                
            button = types.InlineKeyboardButton("Save", callback_data="save_route")
            inline_keyboard.row(button)

            tb.send_message(chat_id, journey, reply_markup=inline_keyboard)

    except:
        tb.send_message(chat_id, "We can not convert your text to a route. Please try again. Be more specific about the addresses you are going to.")




# Initialize and start the Telegram bot session
print("Changes Updated to Chatbot")


tb.infinity_polling(interval=0, timeout=20)
# TelegramMenuSession(API_KEY).start(StartMessage)



