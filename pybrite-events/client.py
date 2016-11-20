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
        self.api_client     = api_client
        self.search_params  = search_params
        self.events         = event_list.get('events')
        pagination          = event_list.get('pagination')
        self.page           = pagination['page_number']
        self.page_count     = pagination['page_count']
        self.page_size      = pagination['page_size']
        self.object_count   = pagination['object_count']
                        
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


class Venues:
    def __init__(self, api_client, location={}):
        self.api_client = api_client
        self.method='venues/{id}/'
        self.location = location
        
    def by_id(self, venue_id):
        return self._send_request(venue_id)
    
    def _send_request(self, venue_id, **search_parameters):
        search_parameters.update(self.location)
        result = self.api_client.find(
            method=self.method.format(id=venue_id),
            **search_parameters
        )
        return result
        

class Events:
    def __init__(self, api_client, with_venues=False, location={}):
        """Initialize with API client. Specify location to limit results.
        
        :param api_client: api client to use for searches
        :param with_venues: Return venue details for each event,
                            rather than just the venue ID.
        :param location: A dictionary with parameters for latitude, longitude,
                         radius. See by_location for more.
        """
        self.api_client = api_client
        self.method = 'events/search/'
        self.location = location  # added to all requests
        self.with_venues = with_venues
        
    def _add_venues(self, event_list):
        venue_ids = {}
        for event in event_list:
            venue_id = event.get('venue_id')
            if venue_ids.get(venue_id) is not None:
                event.update({'venue': venue_ids.get(venue_id)})
            else:
                venue_ids[venue_id] = self.api_client.venues.by_id(venue_id)
                event.update({'venue': venue_ids.get(venue_id)})
        return event_list

                    
    def _send_request(self, **search_parameters):
        search_parameters.update(self.location)
        result = self.api_client.find(
            method=self.method,
            **search_parameters
        )
        if self.with_venues:
            self._add_venues(result.get('events'))
        return Eventerator(self.api_client, result, search_parameters)
    
    def by_keyword(self, keyword):
        return self._send_request(**{'q': keyword})
        
    def by_location(self, latitude, longitude, radius):
        """Find all events in a radius around a latitude/longitude.
        
        :param latitude:
        :param longitude:
        :param radius: Integer followed by "mi" or "ki"
        :return: Events within the area specified
        """
        search_parameters = {
            'location.latitude':    latitude,
            'location.longitude':   longitude,
            'location.within':      radius
        }
        return self._send_request(**search_parameters)
    
    def by_start_date_keyword(self, start_date_keyword):
        """Find events within a timeframe, specified with a keyword.
        
        Keywords:
            today, tomorrow, this_week, next_week, this_weekend,
            this_month, next_month...
        """
        return self._send_request(**{'start_date.keyword': start_date_keyword})
    
    # convenience methods for by_start_date_keyword()
    def today(self):
        return self.by_start_date_keyword('today')
    
    def tomorrow(self):
        return self.by_start_date_keyword('tomorrow')
    
    def this_week(self):
        return self.by_start_date_keyword('this_week')
    
    def next_week(self):
        return self.by_start_date_keyword('next_week')
    
    def this_weekend(self):
        return self.by_start_date_keyword('this_weekend')
    
    def this_month(self):
        return self.by_start_date_keyword('this_month')
    
    def next_month(self):
        return self.by_start_date_keyword('next_month')
    

class ApiClient:
    """Basic API client for Eventbrite API"""
    def __init__(self, auth_token, version='v3', search_location=None):
        """Initialize API client
        
        :param auth_token: eventbrite auth token
        :param version: API version (default: v3)
        :param search_location: Confine all searches to this area. In format
        latitude/longitude/radius (radius being integer followed by 'mi' or 'km')
        """
        self.auth_header = {"Authorization":
                                "Bearer {token}".format(token=auth_token)}
        self.url = base_url.format(version=version)
        self.events = Events(api_client=self, location=search_location)
        self.venues = Venues(api_client=self)
        
    def find(self, method, **search_parameters):
        find_url = "{}{}".format(self.url, method)
        result = requests.get(
            find_url,
            headers=self.auth_header,
            params=search_parameters).json()
        return result
    