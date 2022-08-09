from uptime import uptime
from datetime import timedelta, datetime
import json


DEFAULT_HOSTNAME = "lametric.com"
DEFAULT_PORT = 443


class appRequest:
    """
    This Class reprensents an application request made to the API.
    We log information for statistics purpose.
    """

    def store(self,
                hostname,
                port,
                remoteAddr):

        # clean values
        if not hostname:
            self.hostname = DEFAULT_HOSTNAME

        if not port:
            self.port = DEFAULT_PORT

        self.remoteAddr = remoteAddr
        self.timestamp = datetime.now()

        # store data to DB
        # ...        
        return None


class metrics:
    """
    This Class reprsents the statistics we want to present via the API.
    """
    def __init__(self):
        return None

    def show(self):
        theStats = {
            "Server Uptime": self.setUptime(),
            "Hostname Count": 3456,
            "Last Hostname": "lametric.com",
            "Last Hour Checks": 10
        }
        return json.dumps(theStats)

    def setUptime(self):
        t = uptime()

        # create timedelta and convert it into string
        td_str = str(timedelta(seconds=t))

        # split string into individual component, to be Human Readable
        x = td_str.split(':')
        uptimehr = x[0] + ' Hours, ' + x[1] + ' Minutes'
        return uptimehr 

