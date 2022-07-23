"""Support for Overseerr."""
import logging

import pyoverseerr
import voluptuous as vol
import asyncio
import json

from datetime import timedelta

from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_API_KEY,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SSL,
    CONF_USERNAME,
    CONF_SCAN_INTERVAL,
)
import homeassistant.helpers.config_validation as cv

from homeassistant.helpers.event import track_time_interval

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
DEPENDENCIES = ['webhook']
_LOGGER = logging.getLogger(__name__)
EVENT_RECEIVED = "OVERSEERR_EVENT"


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
                vol.Optional(CONF_SCAN_INTERVAL, default=timedelta(seconds=60)): cv.time_period,
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

    scan_interval=config[DOMAIN][CONF_SCAN_INTERVAL]

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
        movies = overseerr.search_movie(name)["results"]
        if movies:
            movie = movies[0]
            overseerr.request_movie(movie["id"])
        else:
            raise Warning("No movie found.")

    def submit_tv_request(call):
        """Submit request for TV show."""
        name = call.data[ATTR_NAME]
        tv_shows = overseerr.search_tv(name)["results"]

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

    async def update_sensors(event_time):
        """Call to update sensors."""
        _LOGGER.debug("Updating sensors")
        # asyncio.run_coroutine_threadsafe( hass.data[DOMAIN].update(), hass.loop)
        await hass.services.async_call("homeassistant", "update_entity", {ATTR_ENTITY_ID: ["sensor.overseerr_pending_requests"]}, blocking=True)
        await hass.services.async_call("homeassistant", "update_entity", {ATTR_ENTITY_ID: ["sensor.overseerr_movie_requests"]}, blocking=True)
        await hass.services.async_call("homeassistant", "update_entity", {ATTR_ENTITY_ID: ["sensor.overseerr_tv_show_requests"]}, blocking=True)
        await hass.services.async_call("homeassistant", "update_entity", {ATTR_ENTITY_ID: ["sensor.overseerr_issues"]}, blocking=True)
        await hass.services.async_call("homeassistant", "update_entity", {ATTR_ENTITY_ID: ["sensor.overseerr_total_requests"]}, blocking=False)


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
 
    webhook_id = config[DOMAIN].get(CONF_API_KEY)
    _LOGGER.debug("webhook_id: %s", webhook_id)

    _LOGGER.info("Overseerr Installing Webhook")

    hass.components.webhook.async_register(DOMAIN, "Overseerr", webhook_id, handle_webhook)

    url = hass.components.webhook.async_generate_url(webhook_id)
    _LOGGER.debug("webhook data: %s", url)

    # register scan interval
    track_time_interval(hass, update_sensors, scan_interval)

    return True

async def handle_webhook(hass, webhook_id, request):
    """Handle webhook callback."""
    _LOGGER.info("webhook called")

    body = await request.text()
    try:
        data = json.loads(body) if body else {}
    except ValueError:
        return None
    _LOGGER.info("webhook data: %s", body)

    published_data = data
#    published_data['requestid'] = data.get('message')
    _LOGGER.info("webhook data: %s", published_data)
    try:
        if data['notification_type'] == 'MEDIA_PENDING':
            await hass.services.async_call("homeassistant", "update_entity", {ATTR_ENTITY_ID: ["sensor.overseerr_pending_requests"]}, blocking=True)
        if data['media']['media_type'] == 'movie':
            await hass.services.async_call("homeassistant", "update_entity", {ATTR_ENTITY_ID: ["sensor.overseerr_movie_requests"]}, blocking=True)
        if data['media']['media_type'] == 'tv':
            await hass.services.async_call("homeassistant", "update_entity", {ATTR_ENTITY_ID: ["sensor.overseerr_tv_show_requests"]}, blocking=True)
        await hass.services.async_call("homeassistant", "update_entity", {ATTR_ENTITY_ID: ["sensor.overseerr_total_requests"]}, blocking=False)

    except Exception:
        pass

 
    hass.bus.async_fire(EVENT_RECEIVED, published_data)    

