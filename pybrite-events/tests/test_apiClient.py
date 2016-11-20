"""
MIT License

Copyright (c) 2016 - Edward Wells

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from unittest import TestCase
from configparser import ConfigParser
from .. import client
from datetime import datetime


class TestApiClient(TestCase):
    def setUp(self):
        conf = ConfigParser()
        conf.read('config.ini')
        token = conf.get('eventbrite', 'auth_token')
        print('Auth token: {}'.format(token))
        default_location = {
            'location.within': '10mi',
            'location.latitude': '33.7838737',
            'location.longitude': '-84.366088'
        }
        self.eb = client.ApiClient(auth_token=token,
                                   search_location=default_location)
        
    def test_find(self):
        location = {
            'location.within': '10mi',
            'location.latitude': '33.7838737',
            'location.longitude': '-84.366088'
        }
        res = self.eb.find('events/search/', **{'q': 'Atlanta'})
        print(res)
        
    def test_events_by_location(self):
        result = self.eb.events.by_location(
            latitude='33.7838737',
            longitude='-84.366088',
            radius='10mi'
        )
        print(result)
        
    def test_events_by_date(self):
        date_keyword = "this_weekend"
        result = self.eb.events.by_start_date_keyword(date_keyword)
        print(result)
        next_result = result.next()
        print(next_result)
        
    def test_by_date_convenience(self):
        result = self.eb.events.tomorrow()
        print(result)
        
    def test_events_by_keyword(self):
        word = 'Atlanta'
        self.eb.events.with_venues=True
        result = self.eb.events.by_keyword(word)
        print(result)
        
    def test_venue_by_id(self):
        venue_id = '15317054'
        result = self.eb.venues.by_id(venue_id)
        print(result)