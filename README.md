---
title: Overseerr
description: Instructions on how to set up the Overseerr integration in Home Assistant.
ha_category:
  - Sensor
ha_domain: overseerr
---

The `Overseerr` integration monitors data from your [Overseerr](https://overseerr.dev) instance.

## Setup
Install of this component should be done via HACS
* Go into HACS -> Intregrations
* 3 Dots -> Custom Repositories
* Add Custom Repository URL: https://github.com/vaparr/ha-overseerr
* Category: Integration

Restart HA

---

This component needs to authenticate to your Overseerr instance using your `api_key`.

To find your `api_key` open the Overseerr web interface. Navigate to **Settings**, you should then be able to see your `api_key`.


## Configuration

If you want to enable this sensor, add the following lines to your `configuration.yaml`:

```yaml
# Example configuration.yaml entry
overseerr:
  host: OVERSEERR_HOST
  port: OVERSEERR_PORT
  api_key: OVERSEERR_API_KEY
```

{% configuration %}
host:
  description: The hostname or IP Address Overseerr is running on.
  required: true
  type: string
api_key:
  description: Your Overseerr API key. 
  required: true
  type: string
port:
  description: The port Overseerr is running on.
  required: false
  default: 5055
  type: integer
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
  host: 192.168.1.62
  port: 5055
  api_key: MTYwODIpppppppppppppppYzLTI0OqqqqqqqqqqqqzIwLeeeeeee==
```

## Services

### Submit request services

Available services: `submit_movie_request`, `submit_tv_request`

#### Service `submit_movie_request`

Searches and requests the closest matching movie.

| Service data attribute | Optional | Description                                      |
| ---------------------- | -------- | ------------------------------------------------ |
| `name`                 |      no  | Search parameter.                                |                          |

#### Service `submit_tv_request`

Searches and requests the closest matching TV show.

| Service data attribute | Optional | Description                                                                                   |
|------------------------|----------|-----------------------------------------------------------------------------------------------|
| `name`                 |       no | Search parameter.                                                                             |
| `season`               |      yes | Which season(s) to request. Must be one of `first`, `latest` or `all`. Defaults to latest.    |

## WebHook support

You can enable Webhook support in Overseerr to enable faster pending sensor updates.

In overseerr, navigate to Settings -> Noticications > Webhook

Check Enable Agent

for the Webhook URL use:

{{HA SERVER URL}}/api/webhook/{{OVERSEERR API KEY}}

http://homassist.local:8123/api/webhook/MTYwODIpppppppppppppppYzLTI0OqqqqqqqqqqqqzIwLeeeeeee==

Select only the box "Media Requested"

* payload can be left as default


