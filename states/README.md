# States
Here is more documentation about state objects in this folder.

Essentially, states streamline error handling when things go wrong by
implementing a state design pattern, instead of the previous getterCode and
complicated if-statement handlage. In this way, we can make use of
polymorphism to both check for and handle any errors that may happen between
the getter thread and the displayer (main) thread.

**There are 11 states as of the latest update**, starting with state 0.

## Map
* State.py: The parent, abstract, "blueprint" object that handles getters and
  setters as well as several magic methods
* 0 - Waiting.py: We are waiting until it's time to get more JSON. Currently
  the interval is hardcoded to 900s (15 minutes)
* 1 - NoURL.py: Very simply, the URL file couldn't be found on the file system
* 2 - NoGenJSON.py: For whatever reason, general weather JSON couldn't be
  retrieved
* 3 - NoHourJSON.py: For whatever reason, hourly weather JSON couldn't be
  retrieved
* 4 - OutDateJSON.py: NWS provided JSON from a time in the past
* 5 - NewJSON.py: Fresh JSON retrieved from NWS
* 6 - WrongURL.py: HTTP 404 error. Doesn't have to mean a wrong URL, but it
  likely is.
* 7 - ServerError.py: HTTP 503 error
* 8 - NoBackups.py: Due to another error while getting JSON, we looked for
  backup JSON but couldn't find it. We don't really have any information that
  can be displayed now...
* 9 - TooManyErrors.py: Specifically HTTP 500 errors. They generally only last
  a couple seconds but if its been long enough there's probably something
  deeper going on
* 10 - JSONWrongURL.py: Most likely a wrong URL in the URL file. Specifically,
  the JSON library threw a json.decoder.JSONDecodeError