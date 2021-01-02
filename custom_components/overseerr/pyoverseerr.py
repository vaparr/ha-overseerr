"""A python module to retrieve information from Overseerr.

For license information, see the LICENSE.txt file.
"""
import json
import logging

_LOGGER = logging.getLogger(__name__)
_BASE_URL = "http{ssl}://{host}:{port}/{urlbase}api/v1/"


def request(f):
    r = f().json()
    print ("return:", r)
    return r


class Overseerr(object):
    """A class for handling connections with an Overseerr instance."""

    def __init__(
        self, ssl, username, host, port, urlbase="", api_key=None, password=None
    ):

        self._base_url = _BASE_URL.format(
            ssl="s" if ssl else "", host=host, port=port, urlbase=urlbase
        )

        self._api_key = api_key
        self._username = username
        self._password = password
        self._auth = None

    def test_connection(self):
        print ("Testing connections to Overseerr @",self._base_url)
        self._request_connection(path="Settings/Public")

    def _request_connection(self, path, post_data=None, auth=True):
        import requests

        url = f"{self._base_url}{path}"
        headers = {"UserName": self._username}

        if auth:
            headers.update(**self._auth)

        try:
            if post_data is None:
                res = requests.get(url=url, headers=headers, timeout=8)
            else:
                res = requests.post(url=url, headers=headers, json=post_data, timeout=8)

            res.raise_for_status()
            res.json()

            return res

        except TypeError:
            raise OverseerrError("No authentication type set.")
        except requests.exceptions.Timeout:
            raise OverseerrError("Request timed out. Check port configuration.")
        except requests.exceptions.ConnectionError:
            raise OverseerrError("Connection error. Check host configuration.")
        except requests.exceptions.TooManyRedirects:
            raise OverseerrError("Too many redirects.")
        except requests.exceptions.HTTPError as err:
            status = err.response.status_code
            if status == 401:
                raise OverseerrError("Unauthorized error. Check authentication credentials.")
            else:
                raise OverseerrError(f"HTTP Error {status}. Check SSL configuration. {res.json()}")
        except ValueError:
            raise OverseerrError("ValueError. Check urlbase configuration.")

    def authenticate(self):

        if self._api_key:
            self._auth = {"X-Api-Key": self._api_key}
            return

#        credentials = {"userName": self._username, "password": self._password}

#        token = (
#            self._request_connection(path="Token", post_data=credentials, auth=False)
#            .json()
#            .get("access_token")
#        )
#        self._auth = {"Authorization": f"Bearer {token}"}

    def search_movie(self, query):
        return self._request_connection(f"search?query={query}&page=1&language=en").json()

    def search_tv(self, query):
        return self._request_connection(f"search?query={query}&page=1&language=en").json()

    def search_music_album(self, query):
#        return self._request_connection(f"search?query={query}&page=1&language=en").json()
       return

    def request_movie(self, movie_id):
        data = {
            "mediatType": "movie",
            "mediaId": movie_id,
        }
        request(lambda: self._request_connection(path="request", post_data=data))

    def request_tv(
        self, tv_id, request_all=False, request_latest=False, request_first=False
    ):

       tv_data = self._request_connection(f"tv/{tv_id}").json()
       tvdb_id = tv_data['externalIds']['tvdbId']

       if ((request_all == False) and (request_latest == False) and  (request_first == False)):
         request_all = True
       
       if (request_all == True):
         seasons_array = []
         for season in tv_data['seasons']:
           if (season['seasonNumber'] == 0):
             continue
           seasons_array.append(season['seasonNumber'])

       if (request_latest == True):
         for season in tv_data['seasons']:
           latest_season = season['seasonNumber']
         seasons_array = [ latest_season ]

       if (request_first == True):
         seasons_array = [ 1 ]
      
       data = {
            "mediaType": "tv",
            "mediaId": tv_id,
            "tvdbId": tvdb_id,
            "seasons": seasons_array }

       print (data)
       request(lambda: self._request_connection(path="request", post_data=data))

    def request_music(self, album_id):
        #data = {"foreignAlbumId": album_id}
        #request(lambda: self._request_connection(path="Request/music", post_data=data))
        return

    @property
    def movie_requests(self):
        requests = self._request_connection("Request").json()['results']
        i = 0
        for request in requests:
          if request['type'] == "movie":
            i += 1
        return i

    @property
    def tv_requests(self):
        requests = self._request_connection("Request").json()['results']
        i = 0
        for request in requests:
          if request['type'] == "tv":
            i += 1
        return i

    @property
    def music_requests(self):
#        requests = self._request_connection("Request/music/total").text
#        return 0 if requests is None else requests
        return 0

    @property
    def total_requests(self):
        return len(self._request_connection("Request").json()['results'])

    @property
    def available_requests(self):
        return len(self._request_connection("Request?filter=available").json()['results'])

    @property
    def pending_requests(self):
        return len(self._request_connection("Request?filter=pending").json()['results'])

    @property
    def approved_requests(self):
        return len(self._request_connection("Request?filter=approved").json()['results'])

    @property
    def unavailable_requests(self):
        return len(self._request_connection("Request?filter=unavailable").json()['results'])

class OverseerrError(Exception):
    pass
