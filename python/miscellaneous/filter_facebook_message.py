"""
Given a history of messages as returned by Facebook (html-formatted), parses the HTML provided and 
returned all messages sent by a given user, which contain a given piece of text.

This was built to avoid having to go through full history of a conversation with someone manually.

The message-structure has the shape

<div class="message">
    <div class="message_header">
        <span class="user">User1</span>
        <span class="meta">Date1</span>
    </div>
</div>
<p>Message_Content1</p>
<div class="message">
    <div class="message_header">
        <span class="user">User2</span>
        <span class="meta">Date2</span>
    </div>
</div>
<p>Message_Content2</p>
"""

#########################
# Import Global Packages
#########################

# Parse htm strings
from lxml import etree
from cStringIO import StringIO

# handles dates
from datetime import datetime

####################################################################################################
# DEFAULTS
####################################################################################################

# Sets the user / pattern to filter inside the messages.
user_to_filter = 'Username'
message_content_filter = 'http'

# Open htm file provided by facebook containing the messages, and converts it to a tree-like object.
data_file = open('messages.htm', 'r')
magical_parser = etree.XMLParser(encoding='utf-8', recover=True)
content_xml = etree.parse(StringIO(data_file.read()), magical_parser)
data_file.close()

# Dictionnary to sort dates chronologically. Indexed by year, month, day, then time since epoch.
all_messages = {}

# List of all messages where no times could be found.
untimed_messages = []

# Epoch time, to get time since epoch
epoch_time = datetime.utcfromtimestamp(0)


####################################################################################################
# add_message_to_list
####################################################################################################
# Revision History :
#   2016-01-06 AdBa : Function created
####################################################################################################
def add_message_to_list(timestamp, message_text):
    """
    Adds the content of a message in its appropriate location in the message dictionnary structure.

    INPUT:
        timestamp (datetime.datetime) timestamp to use as reference to sort the messages
        message_text (str) content of message to put in structure

    """

    # Gets information from timestamp
    message_year = timestamp.year
    message_month = timestamp.month
    message_day = timestamp.day
    message_time_since_epoch = (timestamp - epoch_time).total_seconds()  # seconds since epoch

    # Creates year key if it is not in the global structure
    if message_year not in all_messages.keys():

        all_messages[message_year] = {}

    # Creates month key if it is not in the year-specific structure
    if message_month not in all_messages[message_year].keys():

        all_messages[message_year][message_month] = {}

    # Creates day key if it is not in the (year, month)-specific structure
    if message_day not in all_messages[message_year][message_month].keys():

        all_messages[message_year][message_month][message_day] = {}

    # Adds message in the (year, month, day) structure, with "seconds_since_epoch" as key.
    all_messages[message_year][message_month][message_day][message_time_since_epoch] = message_text

    #######
    return
    #######

##########################
# END add_message_to_list
##########################


# Goes through all <div> objects, to find those with class "message"
for message in content_xml.iter('div'):

    # If class is not "message", then move on
    if message.get('class') != 'message':

        continue

    # Initializes the date object.
    message_date_as_text = ''

    # Tests if message comes from correct user. By going through metadata (spans) until "class=user"
    #  span is found and the user matches the one to filter
    from_user = False
    for metadata_span in message.iter('span'):

        # Tests if span is the user-metadata.
        if metadata_span.get('class') == 'user':

            # Span the user-metadata. Look at who the user is.
            if metadata_span.text == user_to_filter:

                # User matches the one to filter, so set the 'found' boolean to True
                from_user = True

        # Otherwise, tests if it contains the date, and assigns the date object if it does.
        elif metadata_span.get('class') == 'meta':

            message_date_as_text = metadata_span.text

    # If message was from relevant user, gets <p> tag following <div> tag being analyzed and read it
    if from_user:

        message_content = message.getnext().text

        # If the message content includes the pattern to filter, add message to tree
        if message_content is not None and message_content_filter in message_content:

            # Only add message to tree if date could be parsed, otherwise put in untimed structure
            if message_date_as_text != '':

                # Converts timestamp to datetime.datetime object
                message_date_object = datetime.strptime(message_date_as_text[:-7],
                                                        '%A, %B %d, %Y at %I:%M%p')

                # Adds message in appropriate location
                add_message_to_list(message_date_object, message_content)

            else:

                untimed_messages.append(message_content)


# Outputs messages sorted by time
for year in sorted(all_messages.keys()):

    for month in sorted(all_messages[year].keys()):

        for day in sorted(all_messages[year][month].keys()):

            for time_since_epoch in sorted(all_messages[year][month][day].keys()):

                print '%04d/%02d/%02d : %s' % (year, month, day,
                                               all_messages[year][month][day][time_since_epoch])

# Outputs untimed messages
print('========UNTIMED MESSAGES========')
print(untimed_messages)
