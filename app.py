# flask run --host=0.0.0.0 --port=8000

from flask import Flask, jsonify
from flask_restful import Resource, Api
from flask_restful import reqparse

from urllib.request import Request, urlopen, ssl, socket
from urllib.error import URLError, HTTPError
import datetime
import re

app = Flask(__name__)
app.config['BUNDLE_ERRORS'] = True
api = Api(app)

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('hostname', type=str, required=True)
parser.add_argument('port', type=str, required=True)

class certificate(Resource):
    def get(self):
        args = parser.parse_args()
        hostname = args['hostname']
        port = args['port']

        # Manage wrong app config
        # Remove http:// or https:// using regEx
        hostname = re.sub('http[s]?://', '', hostname, flags=0 )

        # at least, display the app name
        frames = {
                "frames": [
                            {
                            "text": "SSL exp",
                            "icon": "i133"
                            }
                          ]
                    }
                   
        context = ssl.create_default_context()

        try:
            with socket.create_connection((hostname, port)) as sock:
                with context.wrap_socket(sock,
                                         server_hostname=hostname) as ssock:
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

            frames['frames'].append(new_frame)

        except:
            new_frame = {
                        "text": "No info",
                        "icon": "1936"
                        }

            frames['frames'].append(new_frame)

        return jsonify(frames)

api.add_resource(certificate,
                '/certificate/lametric',
                '/certificate')

if __name__ == '__main__':
    app.run
