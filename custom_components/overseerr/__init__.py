"""Support for Overseerr."""
import logging

import pyoverseerr
import voluptuous as vol

from homeassistant.const import (
    CONF_API_KEY,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SSL,
    CONF_USERNAME,
)
import homeassistant.helpers.config_validation as cv

from .const import (
    ATTR_NAME,
    ATTR_SEASON,
    ATTR_ID,
    ATTR_STATUS,
    CONF_URLBASE,
    DEFAULT_PORT,
    DEFAULT_SEASON,
    DEFAULT_SSL,
    DEFAULT_URLBASE,
    DOMAIN,
    SERVICE_MOVIE_REQUEST,
    SERVICE_MUSIC_REQUEST,
    SERVICE_TV_REQUEST,
    SERVICE_UPDATE_REQUEST,
)

_LOGGER = logging.getLogger(__name__)


def urlbase(value) -> str:
    """Validate and transform urlbase."""
    if value is None:
        raise vol.Invalid("string value is None")
    value = str(value).strip("/")
    if not value:
        return value
    return f"{value}/"


SUBMIT_MOVIE_REQUEST_SERVICE_SCHEMA = vol.Schema({vol.Required(ATTR_NAME): cv.string})

SUBMIT_MUSIC_REQUEST_SERVICE_SCHEMA = vol.Schema({vol.Required(ATTR_NAME): cv.string})

SUBMIT_TV_REQUEST_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_NAME): cv.string,
        vol.Optional(ATTR_SEASON, default=DEFAULT_SEASON): vol.In(
            ["first", "latest", "all"]
        ),
    }
)

SERVICE_UPDATE_REQUEST_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ID): cv.positive_int,
        vol.Required(ATTR_STATUS): cv.string,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Optional(CONF_USERNAME): cv.string,
                vol.Required(CONF_API_KEY, "auth"): cv.string,
                vol.Optional(CONF_PASSWORD, "auth"): cv.string,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Optional(CONF_URLBASE, default=DEFAULT_URLBASE): urlbase,
                vol.Optional(CONF_SSL, default=DEFAULT_SSL): cv.boolean,
            },
            cv.has_at_least_one_key("auth"),
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def setup(hass, config):
    """Set up the Overseerr component platform."""

    overseerr = pyoverseerr.Overseerr(
        ssl=config[DOMAIN][CONF_SSL],
        host=config[DOMAIN][CONF_HOST],
        port=config[DOMAIN][CONF_PORT],
        urlbase=config[DOMAIN][CONF_URLBASE],
        username=config[DOMAIN].get(CONF_USERNAME),
        password=config[DOMAIN].get(CONF_PASSWORD),
        api_key=config[DOMAIN].get(CONF_API_KEY),
    )

    try:
        overseerr.authenticate()
        overseerr.test_connection()
    except pyoverseerr.OverseerrError as err:
        _LOGGER.warning("Unable to setup Overseerr: %s", err)
        return False

    hass.data[DOMAIN] = {"instance": overseerr}

    def submit_movie_request(call):
        """Submit request for movie."""
        name = call.data[ATTR_NAME]
        movies = overseerr.search_movie(name)
        if movies:
            movie = movies[0]
            overseerr.request_movie(movie["theMovieDbId"])
        else:
            raise Warning("No movie found.")

    def submit_tv_request(call):
        """Submit request for TV show."""
        name = call.data[ATTR_NAME]
        tv_shows = overseerr.search_tv(name)

        if tv_shows:
            season = call.data[ATTR_SEASON]
            show = tv_shows[0]["id"]
            if season == "first":
                overseerr.request_tv(show, request_first=True)
            elif season == "latest":
                overseerr.request_tv(show, request_latest=True)
            elif season == "all":
                overseerr.request_tv(show, request_all=True)
        else:
            raise Warning("No TV show found.")

    def submit_music_request(call):
        """Submit request for music album."""
        name = call.data[ATTR_NAME]
        music = overseerr.search_music_album(name)
        if music:
            overseerr.request_music(music[0]["foreignAlbumId"])
        else:
            raise Warning("No music album found.")

    def update_request(call):
        """Update status of specified request."""
        request_id = call.data[ATTR_ID]
        status = call.data[ATTR_STATUS]
        overseerr.update_request(request_id, status)

    hass.services.register(
        DOMAIN,
        SERVICE_MOVIE_REQUEST,
        submit_movie_request,
        schema=SUBMIT_MOVIE_REQUEST_SERVICE_SCHEMA,
    )
    hass.services.register(
        DOMAIN,
        SERVICE_MUSIC_REQUEST,
        submit_music_request,
        schema=SUBMIT_MUSIC_REQUEST_SERVICE_SCHEMA,
    )
    hass.services.register(
        DOMAIN,
        SERVICE_TV_REQUEST,
        submit_tv_request,
        schema=SUBMIT_TV_REQUEST_SERVICE_SCHEMA,
    )
    hass.services.register(
        DOMAIN,
        SERVICE_UPDATE_REQUEST,
        update_request,
        schema=SERVICE_UPDATE_REQUEST_SCHEMA,
    )    
    hass.helpers.discovery.load_platform("sensor", DOMAIN, {}, config)

    return True
