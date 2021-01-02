---
title: Overseerr
description: Instructions on how to set up the Overseerr integration in Home Assistant.
ha_category:
  - Sensor
ha_release: '0.100'
ha_iot_class: Local Polling
ha_codeowners:
  - '@larssont'
ha_domain: overseerr
---

The `Overseerr` integration monitors data from your [Overseerr](https://overseerr.io) instance.

## Setup

This component needs to authenticate to your Overseerr instance with either a user `password` or an `api_key`.

To find your `api_key` open the Overseerr web interface. Navigate to **Settings** and then to **Overseerr**, you should then be able to see your `api_key`.

If you want to use `password` authentication simply use the same `password` you normally use to login to Overseerr. Alternatively, you can set up a separate local account in Overseerr designated for Home Assistant. In order to do this, open the Overseerr web interface. Navigate to **User Management** and then press **Add User To Overseerr**. Input your desired user details and use the same details when configuring this integration.

## Configuration

If you want to enable this sensor, add the following lines to your `configuration.yaml`:

```yaml
# Example configuration.yaml entry
overseerr:
  host: OVERSEERR_HOST
  username: OVERSEERR_USERNAME
  password: OVERSEERR_PASSWORD
```

{% configuration %}
host:
  description: The hostname or IP Address Overseerr is running on.
  required: true
  type: string
username:
  description: Your Overseerr username.
  required: true
  type: string
password:
  description: Your Overseerr password. [`password`](#password) and [`api_key`](#api_key) cannot be specified concurrently.
  required: exclusive
  type: string
api_key:
  description: Your Overseerr API key. [`password`](#password) and [`api_key`](#api_key) cannot be specified concurrently.
  required: exclusive
  type: string
port:
  description: The port Overseerr is running on.
  required: false
  default: 5000
  type: integer
urlbase:
  description: The Base URL path of your Overseerr instance.
  required: false
  type: string
ssl:
  description: Whether or not to use SSL when connecting to Overseerr.
  required: false
  default: false
  type: boolean
{% endconfiguration %}

## Full example for the configuration

```yaml
# Example configuration.yaml entry
overseerr:
  host: OVERSEERR_HOST
  username: OVERSEERR_USERNAME
  api_key: OVERSEERR_API_KEY
  port: OVERSEERR_PORT
  urlbase: overseerr/
  ssl: true
```

## Services

### Submit request services

Available services: `submit_movie_request`, `submit_music_request`, `submit_tv_request`

#### Service `submit_movie_request`

Searches and requests the closest matching movie.

| Service data attribute | Optional | Description                                      |
| ---------------------- | -------- | ------------------------------------------------ |
| `name`                 |      no  | Search parameter.                                |

#### Service `submit_music_request`

Searches and requests the closest matching music album.

| Service data attribute | Optional | Description                                      |
|------------------------|----------|--------------------------------------------------|
| `name`                 |      no  | Search parameter.                                |

#### Service `submit_tv_request`

Searches and requests the closest matching TV show.

| Service data attribute | Optional | Description                                                                                   |
|------------------------|----------|-----------------------------------------------------------------------------------------------|
| `name`                 |       no | Search parameter.                                                                             |
| `season`               |      yes | Which season(s) to request. Must be one of `first`, `latest` or `all`. Defaults to latest.    |
