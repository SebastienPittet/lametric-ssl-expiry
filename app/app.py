from flask import Flask, send_from_directory
from flask import jsonify, render_template, request
from urllib.request import ssl, socket
import datetime
import re
from metrics import metrics

ssl_expiry_app = Flask(__name__)


default_hostname = "lametric.com"
default_port = "443"


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
        self.hostname = re.sub('http[s]?://', '', self.hostname, flags=0)
        self.hostname = self.hostname.strip()  # remove whitespaces

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
                    cert = ssock.getpeercert()

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

        except OSError:
            new_frame = {
                        "text": "No Info",
                        "icon": "1936"
                        }

            self.frames['frames'].append(new_frame)

        return jsonify(self.frames)


@ssl_expiry_app.route("/api/v1", methods=['GET'])
def check_certificate():
    hostname = request.args.get("hostname")
    port = request.args.get("port")

    # collect info for statistics
    try:
        recording = metrics()
        recording.storeDB(hostname,
                          port,
                          request.remote_addr,
                          )
    except Exception as e:
        # Do something in case of error
        print(e)

    myCert = certificate(hostname, port)
    return myCert.check()


@ssl_expiry_app.route("/", methods=['GET'])
def webFrontEnd():
    return render_template('index.html')


@ssl_expiry_app.route("/api/v1/metrics", methods=['GET'])
def statistics():
    stats = metrics()
    return stats.show()


# Testing to check if it works
@ssl_expiry_app.route('/test')
def test():
    return "OK!"

@ssl_expiry_app.route('/robots.txt')
@ssl_expiry_app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(ssl_expiry_app.static_folder, request.path[1:])

if __name__ == '__main__':
    ssl_expiry_app.run()
