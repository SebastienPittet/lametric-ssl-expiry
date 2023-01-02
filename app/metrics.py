from uptime import uptime
from datetime import timedelta, datetime
import json
import database

DEFAULT_HOSTNAME = "lametric.com"
DEFAULT_PORT = 443


class metrics:
    """
    This Class represents the statistics we want to present via the API.
    """
    def __init__(self):
        """
        init DB and get values.
        In case of error, set error values
        """
        self.hostname = DEFAULT_HOSTNAME
        self.port = DEFAULT_PORT
        self.timestamp = ""
        self.remoteAddr = ""
        return None

    def setUptime(self):
        t = uptime()

        # create timedelta and convert it into string
        td_str = str(timedelta(seconds=t))

        # split string into individual component, to be Human Readable
        x = td_str.split(':')
        uptimehr = x[0] + ' Hours, ' + x[1] + ' Minutes'
        return uptimehr

    def show(self):
        """
        Get values and prepare for display
        """
        theStats = database.GetDB()
        # Add the server uptime
        theStats["Server Uptime"] = self.setUptime()
        return json.dumps(theStats)

    def storeDB(self,
                hostname,
                port,
                remoteAddr):
        """
        We store information in DB for statistics purpose.
        """
        # clean values
        if not hostname:
            self.hostname = DEFAULT_HOSTNAME
        else:
            self.hostname = hostname

        if not port:
            self.port = DEFAULT_PORT
        else:
            self.port = port

        self.remoteAddr = remoteAddr

        current_time = datetime.now()
        self.timestamp = current_time.timestamp()

        database.StoreDB(self.hostname,
                         self.port,
                         self.timestamp,
                         self.remoteAddr)
        return None
