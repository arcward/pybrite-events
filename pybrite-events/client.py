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
import requests

base_url = "https://www.eventbriteapi.com/{version}/"


# class Events:
#     def __init__(self, api_client):
#         self.api_client = api_client
#         self.search_url =
#
#     def search(self):
        

class Events:
    def __init__(self, api_client):
        self.api_client = api_client
        self.method = 'events/search/'
        
    def by_location(self, latitude, longitude, radius):
        search_parameters = {
            'location.latitude': latitude,
            'location.longitude': longitude,
            'location.within': radius
        }
        return self.api_client.find(method=self.method,
                                    **search_parameters)
    
    def by_start_date_keyword(self, start_date_keyword):
        return self.api_client.find(self.method,
                                    **{'start_date.keyword': start_date_keyword})


class ApiClient:
    def __init__(self, auth_token, version='v3'):
        self.auth_header = {
            "Authorization":
                "Bearer {token}".format(token=auth_token)
        }
        self.url = base_url.format(version=version)
        methods = {'event': 'events/', 'venue': 'venues/'}
        
        self.events = Events(api_client=self)
        
    def find(self, method, **search_parameters):
        find_url = "{}{}".format(self.url, method)
        result = requests.get(
            find_url,
            headers=self.auth_header,
            params=search_parameters).json()
        return result
    