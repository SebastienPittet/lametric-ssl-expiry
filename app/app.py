from app import app
from flask import jsonify, render_template, request
from urllib.request import ssl, socket
import datetime
import re
from . import metrics


default_hostname = "lametric.com"
default_port     = "443"

class certificate:
    """
    The aim of this class is to check the expiry of
    a certificate for a given hostname.
    """
    def __init__(self, hostname=default_hostname, port=default_port):
        """
        Init. Help text here
        Clean-up of the data provided.  
        """
        self.hostname = hostname
        self.port = port

        if not self.port:
            # set default value if empty
            self.port = "443"

        if not self.hostname:
            # set default value if empty
            self.hostname = "lametric.com"

        # Manage wrong app config
        # Remove http:// or https:// using regEx
        self.hostname = re.sub('http[s]?://', '', self.hostname, flags=0 )

       # at least, display the app name. Init of the LAMETRIC frames.
        self.frames = {
                "frames": [
                            {
                            "text": "SSL exp",
                            "icon": "i133"
                            }
                          ]
                    }
        return


    def check(self):
        context = ssl.create_default_context()

        try:
            with socket.create_connection((self.hostname, self.port)) as sock:
                with context.wrap_socket(sock,
                                         server_hostname=self.hostname) as ssock:
                    cert=ssock.getpeercert()

                    # Find expiration date
                    exp_date = cert['notAfter']

            expiry = datetime.datetime.strptime(exp_date, '%b %d %X %Y %Z')
            today = datetime.datetime.today()
            delta = expiry - today

            # Build the frame
            new_frame = {
                        "text": str(delta.days) + " days",
                        "icon": "a464"
                        }

            self.frames['frames'].append(new_frame)

        except OSError as error:
            new_frame = {
                        "text": "No Info",
                        "icon": "1936"
                        }

            self.frames['frames'].append(new_frame)
        
        return jsonify(self.frames)


@app.route("/api/v1", methods=['GET'])
def check_certificate():
    hostname = request.args.get("hostname")
    port = request.args.get("port")
    
    # collect info for statistics
    try:
        recording = metrics.metrics()
        recording.storeDB(hostname,
                          port,
                          request.remote_addr,
                        )
    except Exception as e:
        # Do something in case of error
        print(e)

    myCert = certificate(hostname, port)
    return myCert.check()


@app.route("/", methods=['GET'])
def webFrontEnd():
    return render_template('index.html')


@app.route("/api/v1/metrics", methods=['GET'])
def statistics():
    stats = metrics.metrics()
    return stats.show()


# Testing to check if it works
@app.route('/test')
def test():
    return "OK!"


if __name__ == '__main__':
    app.run()
