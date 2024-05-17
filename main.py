#    Copyright 2024 Sakan Nirattisaykul
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from loguru import logger

from japan_avg_hotel_price_finder.scrape_each_date import ScrapeEachDate
from japan_avg_hotel_price_finder.thread_scrape import ThreadScrape

logger.add('japan_avg_hotel_price_month.log',
           format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {name} | {module} | {function} | {line} | {message}",
           mode='w')

# Define booking parameters for the hotel search.
city = 'Osaka'
group_adults = '1'
num_rooms = '1'
group_children = '0'
selected_currency = 'USD'

# Specify the start date and duration of stay for data scraping
start_day = 1
month = 8
year = 2024
nights = 1

# scrape_each_date = ScrapeEachDate(city, group_adults, num_rooms, group_children, selected_currency)
# scrape_each_date.scrape_until_month_end(start_day, month, year, nights)

thread_scrape = ThreadScrape(city, group_adults, num_rooms, group_children, selected_currency, start_day, month, year,
                             nights)
thread_scrape.thread_scrape()
