"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""
from __future__ import print_function
import time
from datetime import datetime
import requests
from lxml import etree
import pytz


def mps_to_mph(mps):
    return 2.23694 * mps


def deg_to_compass(num):
    val = int((num/22.5)+.5)
    arr = ["N","NNE","NE","ENE","E","ESE", "SE", "SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
    return arr[(val % 16)]


def state_washington(body_of_water):
    water_temp_url = 'https://green2.kingcounty.gov/lake-buoy/DataScrape.aspx?type=profile&buoy={}&year={}&month={}'
    air_temp_url = 'https://green2.kingcounty.gov/lake-buoy/DataScrape.aspx?type=met&buoy={}&year={}&month={}'

    if body_of_water == 'lake washington':
        buoy = 'wa'
    elif body_of_water == 'lake sammamish':
        buoy = 'samm'
    else:
        return "I'm sorry, I couldn't find that body of water"

    current_month = time.strftime("%m")
    current_year = time.strftime("%Y")

    # First let's get the water temperature from the buoy data
    # We're going to get back this awesome ASPX table that we'll have to disect
    url_to_use = water_temp_url.format(buoy, current_year, current_month)
    r = requests.get(url_to_use)
    table_start = r.content.find('<table')
    table_end = r.content.find('</table>') + 8
    table_string = r.content[table_start:table_end]

    # Now we have the string from the response that is the table.
    # Let's look for the latest temp at a reasonable (< 1.5m) depth. Record the date/time/temp
    latest_date_water_temp = datetime.strptime('01/01/2000', "%m/%d/%Y")
    # latest_depth = 0
    latest_temp_water = 0

    table = etree.XML(table_string)
    rows = iter(table)
    headers = [col.text for col in next(rows)]
    for row in rows:
        values = [col.text for col in row]
        row_dict = dict(zip(headers, values))
        if float(row_dict.get('Depth (m)')) < 1.5:
            temp_c = float(row_dict.get(u'Temperature (\xb0C)'))
            temp_f = temp_c * 1.8 + 32
            date_object = datetime.strptime(row_dict.get('Date'), "%m/%d/%Y %I:%M:%S %p")
            if date_object >= latest_date_water_temp:
                latest_date_water_temp = date_object
                # latest_depth = row_dict.get('Depth (m)')
                latest_temp_water = temp_f
    # Excellent, now we have our most recent water temp
    latest_temp_water = round(latest_temp_water, 1)

    # Now let's get the air temperature from the buoy data
    # We're going to get back this awesome ASPX table that we'll have to disect
    url_to_use = air_temp_url.format(buoy, current_year, current_month)
    r = requests.get(url_to_use)
    table_start = r.content.find('<table')
    table_end = r.content.find('</table>') + 8
    table_string = r.content[table_start:table_end]

    # Now we have the string from the response that is the table.
    # Let's look for the latest temp at a reasonable (< 1.5m) depth. Record the date/time/temp
    latest_date_air_temp = datetime.strptime('01/01/2000', "%m/%d/%Y")
    latest_temp_air = 0
    latest_wind_air_speed = 0
    latest_wind_air_dir = ''

    table = etree.XML(table_string)
    rows = iter(table)
    headers = [col.text for col in next(rows)]
    for row in rows:
        values = [col.text for col in row]
        row_dict = dict(zip(headers, values))
        temp_c = float(row_dict.get(u'Air Temperature (\xb0C)'))
        temp_f = temp_c * 1.8 + 32
        date_object = datetime.strptime(row_dict.get('Date'), "%m/%d/%Y %I:%M:%S %p")
        if date_object >= latest_date_air_temp:
            latest_date_air_temp = date_object
            latest_temp_air = temp_f
            latest_wind_air_speed = float(row_dict.get(u'Wind Speed (m/sec)'))
            latest_wind_air_dir = float(row_dict.get(u'Wind Direction (degrees)'))
    # Excellent, now we have our most recent water temp
    latest_temp_air = round(latest_temp_air, 1)

    if latest_date_water_temp == datetime.strptime('01/01/2000', "%m/%d/%Y") and \
       latest_date_air_temp == datetime.strptime('01/01/2000', "%m/%d/%Y"):
        # This means we didn't find anythiing
        retval = "I'm sorry, I couldn't find any recent data about the weather on {}".format(body_of_water)
    else:
        retval = "Last known conditions on {} include: ".format(body_of_water)
        num_values = 0
        if latest_date_water_temp != datetime.strptime('01/01/2000', "%m/%d/%Y"):
            # Need to make this aware of the time zone
            tz = pytz.timezone('US/Pacific')
            latest_date_tz = tz.localize(latest_date_water_temp)
            time_diff = datetime.now(tz) - latest_date_tz
            # time_diff = datetime.now() - latest_date_water_temp
            if time_diff.days > 0:
                hours_diff = time_diff.days * 24
                hours_diff += time_diff.seconds / 60 / 60
            else:
                hours_diff = time_diff.seconds / 60 / 60
            retval += "Water temperature of {} degrees fahrenheit, about {} hours ago".format(latest_temp_water, hours_diff)
            num_values += 1
        if latest_date_air_temp != datetime.strptime('01/01/2000', "%m/%d/%Y"):
            # Need to make this aware of the time zone
            tz = pytz.timezone('US/Pacific')
            latest_date_tz = tz.localize(latest_date_air_temp)
            time_diff = datetime.now(tz) - latest_date_tz
            # time_diff = datetime.now() - latest_date_water_temp
            if time_diff.days > 0:
                hours_diff = time_diff.days * 24
                hours_diff += time_diff.seconds / 60 / 60
            else:
                hours_diff = time_diff.seconds / 60 / 60
            if num_values > 0:
                retval += " and "
            retval += "Air temperature of {} degrees fahrenheit, ".format(latest_temp_air)
            retval += "wind speed of {} ".format(round(mps_to_mph(latest_wind_air_speed), 1))
            retval += "coming from the {},".format(latest_wind_air_dir)
            retval += "about {} hours ago".format(hours_diff)
    return retval

# --------------- Some GLOBALS that need to come after we define the state functions ----------------------
BODIES_OF_WATER = dict()
BODIES_OF_WATER["lake washington"] = state_washington
BODIES_OF_WATER["lake sammamish"] = state_washington


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Marshall. " \
                    "Please tell me what body of water you'd like to know the weather for."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me what body of water you'd like to know the weather for."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thanks, and have a great day on the water!"
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def get_weather(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Body_Of_Water' in intent['slots']:
        body_of_water = intent['slots']['Body_Of_Water']['value'].lower()
        if body_of_water in BODIES_OF_WATER:
            speech_output = BODIES_OF_WATER[body_of_water](body_of_water)
            should_end_session = True
        else:
            speech_output = "I don't know that body of water"
        reprompt_text = "Please, Tell me again what body of water you are interested in."
    else:
        speech_output = "I don't know that body of water"
        reprompt_text = "Please, Tell me again what body of water you are interested in."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "GetWeatherIntent":
        return get_weather(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.3288ae1b-9739-4308-8f09-d0802a8a85c9"):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])

    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])

    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
