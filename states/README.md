# States
Here is more documentation about state objects in this folder.

Essentially, states streamline error handling when things go wrong by
implementing a state design pattern, instead of the previous getterCode and
complicated if-statement handlage. In this way, we can make use of
polymorphism to both check for and handle any errors that may happen between
the getter thread and the displayer (main) thread.

**There are 12 states as of the latest update**, starting with state 0.

## Map
* State.py: The parent, abstract, "blueprint" object that handles getters and
  setters as well as several magic methods
* 0 - Waiting: We are waiting until it's time to get more JSON. Currently
  the interval is hardcoded to 900s (15 minutes)
* 1 - NoURL: Very simply, the URL file couldn't be found on the file system
* 2 - NoGenJSON: For whatever reason, general weather JSON couldn't be
  retrieved
* 3 - NoHourJSON: For whatever reason, hourly weather JSON couldn't be
  retrieved
* 4 - OutDateJSON: NWS provided JSON from a time in the past
* 5 - NewJSON: Fresh JSON retrieved from NWS
* 6 - WrongURL: HTTP 404 error. Doesn't have to mean a wrong URL, but it
  likely is.
* 7 - ServerError: HTTP 503 error
* 8 - NoBackups: Due to another error while getting JSON, we looked for
  backup JSON but couldn't find it. We don't really have any information that
  can be displayed now...
* 9 - TooManyErrors: Specifically HTTP 500 errors. They generally only last
  a couple seconds but if its been long enough there's probably something
  deeper going on
* 10 - JSONWrongURL: Most likely a wrong URL in the URL file. Specifically,
  the JSON library threw a json.decoder.JSONDecodeError
* 11 - InvalidURL: Provided URL is either empty or doesn't fit the standard
  HTTP URL format (e.g. https://subdomain.domain.com)
* 12 - GetterEnded: Non-fatal state to keep display running when Getter isn't,
  mainly used when a 503 error is detected but crashOnHTTPError is off
* 13 - ErrorHandled: There was a fatal error that was handled, and now
  Weather-Displayer should close. Used mostly for threads to handle errors
  in their own way