import requests
from lxml import etree
from datetime import datetime
import time
import pytz

SAMMAISH = 'samm'
WASHINGTON = 'wa'
LAKE = WASHINGTON
URL = 'https://green2.kingcounty.gov/lake-buoy/DataScrape.aspx?type=profile&buoy={}&year={}&month={}'
# https://green2.kingcounty.gov/lake-buoy/DataScrape.aspx?type=met&buoy=wa&year=2016&month=10

# current_day = time.strftime("%d")
current_month = time.strftime("%m")
current_year = time.strftime("%Y")
url = URL.format(LAKE, current_year, current_month)
print url
r = requests.get(url)

table_start = r.content.find('<table')
table_end = r.content.find('</table>') + 8
table_string = r.content[table_start:table_end]

latest_date = datetime.strptime('01/01/2000', "%m/%d/%Y")
latest_depth = 0
latest_temp = 0

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
        if date_object >= latest_date:
            latest_date = date_object
            latest_depth = row_dict.get('Depth (m)')
            latest_temp = temp_f

tz = pytz.timezone('US/Pacific')
dt_aware = tz.localize(latest_date)
time_diff = datetime.now(tz) - dt_aware
# time_diff = datetime.now() - latest_date
if time_diff.days > 0:
    hours_diff = time_diff.days * 24
    hours_diff += time_diff.seconds / 60 / 60
else:
    hours_diff = time_diff.seconds / 60 / 60

print hours_diff

print "Date: {}, Depth (m): {}, Temp: {}".format(latest_date, latest_depth, round(latest_temp, 1))
print round(latest_temp, 1)

