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


class Eventerator:
    """Iterator for event search results.
    Handles paginated API responses."""
    def __init__(self, api_client, event_list, search_params):
        # Keep client/params on hand to request the next page
        self.api_client = api_client
        self.events = event_list.get('events')
        self.search_params = search_params
        # 'Paginated' dict in API response
        pagination = event_list.get('pagination')
        self.page = pagination['page_number']
        self.page_count = pagination['page_count']
        self.page_size = pagination['page_size']
        self.object_count = pagination['object_count']
                        
    def next(self):
        """Returns the next page of a paginatied response, if there is one."""
        if self.page <= self.page_count:
            self.page += 1
            self.search_params.update({'page': self.page})
            return self.api_client.events._send_request(**self.search_params)
        else:
            raise StopIteration()


        def __iter__(self):
            return self


class Events:
    def __init__(self, api_client, location={}):
        """Initialize with API client. Specify location to limit results.
        :param api_client:
        :param location: A dictionary with parameters for latitude, longitude,
        radius. See by_location for more.
        """
        self.api_client = api_client
        self.method = 'events/search/'
        self.universal_params = {}.update(location)  # added to all searches
        
    def _send_request(self, **search_parameters):
        result = self.api_client.find(method=self.method,
                                      **search_parameters)
        return Eventerator(self.api_client, result, search_parameters)
        
    def by_location(self, latitude, longitude, radius):
        """Find all events in a radius around a latitude/longitude.
        
        :param latitude:
        :param longitude:
        :param radius: Integer followed by "mi" or "ki"
        :return: Events within the area specified
        """
        search_parameters = {
            'location.latitude': latitude,
            'location.longitude': longitude,
            'location.within': radius
        }
        return self._send_request(**search_parameters)
    
    def by_start_date_keyword(self, start_date_keyword):
        """Find events within a timeframe, specified with a keyword.
        
        Keywords:
            tomorrow, today, this_week, next_week, this_weekend,
            this_month, next_month...
        """
        return self._send_request(**{'start_date.keyword': start_date_keyword})


class ApiClient:
    """Basic API client for Eventbrite API"""
    def __init__(self, auth_token, version='v3'):
        self.auth_header = {
            "Authorization":
                "Bearer {token}".format(token=auth_token)
        }
        self.url = base_url.format(version=version)
        methods = {'event': 'events/', 'venue': 'venues/'}
        
        self.events = Events(api_client=self)
        
    def paginate(self):
        """Handles pagination
        See: https://www.eventbrite.com/developer/v3/reference/pagination/
        """
        pass
        
    def find(self, method, **search_parameters):
        find_url = "{}{}".format(self.url, method)
        result = requests.get(
            find_url,
            headers=self.auth_header,
            params=search_parameters).json()
        return result
    