## Setup & run

### Local env
`make install` - one off command to install the app env and dependencies.
`make run` - run the app (debug logging off).
`make debug` - run the app with debug logging on.
`make clean` - removes all the temporary files, virtual env, etc.

### Docker container

Simply run `docker-compose up --build` and then navigate to app in your web-browser, e.g.
`http://localhost:8000/search?starts_at=2020-05-01T17:32:28Z&ends_at=2023-07-21T17:32:28Z`

## Tech stack

Because of the requirement to have the service as resource and time efficient as possible, I chose following tech stack (note that everything below comes with FastAPI installation):

* [FastAPI](https://fastapi.tiangolo.com/) - is a modern, fast (high-performance), web framework for building APIs with Python 3.8+ based on standard Python type hints. [One of the fastest Python frameworks](https://fastapi.tiangolo.com/benchmarks/) available.
* [Uvicorn](https://www.uvicorn.org/) - is an ASGI web server implementation for Python. Supports async concurrency operations, so it significantly improves speed on returning response back to client.
* [Pydantic](https://docs.pydantic.dev/latest/) - performs data validation over defined models
* [HTTPX](https://www.python-httpx.org/quickstart/) - asyncronous http requests library
* [lxml](https://lxml.de/) - fast and effective parsing of xml documents


## API docs

Simple run the app with uvicorn, then go to http://127.0.0.1:8000/docs

Don't forget to update `swagger.yaml` once you have changed your online [API spec](https://app.swaggerhub.com/apis-docs/luis-pintado-feverup/backend-test/1.0.0). Use [this link](https://api.swaggerhub.com/apis/luis-pintado-feverup/backend-test/1.0.0/swagger.yaml) to download yaml.


## Assumptions

1. The app has been written with Python 3.11.6; Backward compatibility is not guaranteed.
2. Implementation focused on performance (in some places at the cost of consuming additional memory).
3. Assume that both backend query requests `starts_at`/`ends_at` and Event Partner API xml attrs `event_start_date`/`event_end_date` datetimes are in UTC time zone.
4. Assume that there could be several events under the same base_event (e.g., the same title/show, but on different dates/times).

## Data formats

Below you can find matching between different input/output formats.

##### Partner API response (xml)
This structure is provided as is by "[partner API](https://provider.code-challenge.feverup.com/api/events)".
```xml
<eventList xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.0" xsi:noNamespaceSchemaLocation="eventList.xsd">
  <output>
    <base_event base_event_id="1591" sell_mode="online" organizer_company_id="1" title="Los Morancos">
      <event event_start_date="2021-07-31T20:00:00"
         event_end_date="2021-07-31T21:00:00"
         event_id="1642"
         sell_from="2021-06-26T00:00:00"
         sell_to="2021-07-31T19:50:00"
         sold_out="false">
          <zone zone_id="186" capacity="0" price="75.00" name="Amfiteatre" numbered="true"/>
          <zone zone_id="186" capacity="12" price="65.00" name="Amfiteatre" numbered="false"/>
      </event>
    </base_event>
  </output>
</eventList>
```

##### DB

Simple in-memory dict storage, could be upgraded later without change in structure, e.g. to use Redis, MongoDB or other solution.

```python
{
    # Event key: Base Event + Original event ID from partner API.
    # To identify partner Event.
    (1591, 1642): {
      # UUID for response instead original event ID,
      # automatically generated on first insert to storage.
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "title": "Los Morancos",
      "start_date": "2021-07-31",
      "start_time": "20:00:00",
      "end_date": "2021-07-31",
      "end_time": "21:00:00",
      "min_price": 65.00,
      "max_price": 75.00,
      # event.start and event.end datetime objects. For filtering.
      "start": datetime.datetime object,
      "end": datetime.datetime object,
    },
}
```

##### App API response (json)
This structure comes from app OpenAPI [spec](https://app.swaggerhub.com/apis-docs/luis-pintado-feverup/backend-test/1.0.0#/default/searchEvents).
```json{
  "data": {
    "events": [
      {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "title": "Los Morancos",
        "start_date": "2021-07-31",
        "start_time": "20:00:00",
        "end_date": "2021-07-31",
        "end_time": "21:00:00",
        "min_price": 65.00,
        "max_price": 75.00,
      }
    ]
  },
  "error": null
}
```

## Performance

It's worth to note that this is a prototype app and real production environment may include many additional things like caches, load balancers, service discovery, API gateways, etc.

Neverthless, some design decisions allowed to reach good response time while decouple user request/response from other (Partner) API availability.

* First, for prototype I used very simple in-memory storage that holds previously fetched events data.
* Then, for Partner API calls I used async/await pattern so that server do not blocks here and may switch to other requests/tasks while waiting response.
* Finally, `handle_new_events_request` (which requests partner event data from external API, parses XML and then stores result data) processed asynchronously in background task, allowing us return response to user with very low latency, however, by cost of eventual consistency (the updated data will be available on the next user request).

Request response time metrics I have on my environment (call to `/search` handler):

    With background tasks (current design):
    Function run in (ms):  0.241        first request (after app started)
    Function run in (ms):  0.145        mean on subsequent requests

    Without background tasks (but with await on i/o operations like network requests):
    Function run in (ms):  271.899        first request (after app started)
    Function run in (ms):  236.283        mean on subsequent requests
