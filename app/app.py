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
        To instanciate this class, hostname and TCP port are required.
        Clean-up of the data provided and create the first LAMETRIC frame.
        """
        self.port = port

        if not self.port:
            # set default value if empty
            self.port = default_port

        self.hostname = hostname

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
        """
        Create a connection and get the exiry date.
        Compute the remaining number of days.
        Construct and append the LAMETRIC frame.
        """
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

def get_hostname(str_hostname = default_hostname):
    # Remove whitespace and trailing slash if present
    str_hostname = str_hostname.strip().rstrip('/')

    # Remove the "https://" prefix if present
    if str_hostname.startswith('https://'):
        str_hostname = str_hostname[8:]
    
    # Defined the regular expression pattern for a FQDN
    # with great help of https://regex-generator.olafneumann.org/

    # Find FQDN in the test string
    pattern = r'^(?:[a-z0-9]+\.)+[a-z0-9]{2,}$'
    match = re.match(pattern, str_hostname)

    if match:
        return match.group(0)
    else:
        return None

@ssl_expiry_app.route("/api/v1", methods=['GET'])
def check_certificate():
    hostname = request.args.get("hostname")
    hostname = get_hostname(hostname)

    port = request.args.get("port")

    # Collect info for statistics
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

@ssl_expiry_app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

if __name__ == '__main__':
    ssl_expiry_app.run()
