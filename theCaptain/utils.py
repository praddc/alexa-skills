# This takes in Meters Per Second and returns Miles Per Hour
def mps_to_mph(mps):
    return 2.23694 * mps


# This converts from degrees to a direction on a compass
def deg_to_compass(num):
    val = int((num/22.5)+.5)
    arr = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    return arr[(val % 16)]


# This translates compass directions into a string that the Alexa Skills Kit can verbalize
def compass_to_words(direction):
    # Start with nothing
    retval = ''

    # Get rid of the word 'by' if it's in there
    if direction.find('by') >= 0:
        direction.replace('by', '')
    # Get rid of any spaces
    direction.replace(' ', '')

    for letter in direction:
        if letter.upper() == 'N':
            retval += 'north '
        elif letter.upper() == 'E':
            retval += 'east '
        elif letter.upper() == 'S':
            retval += 'south '
        elif letter.upper() == 'W':
            retval += 'west '
    return retval

