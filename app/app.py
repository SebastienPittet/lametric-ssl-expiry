from flask import Flask, send_from_directory
from flask import jsonify, render_template, request
from dataclasses import dataclass, field
from urllib.request import ssl, socket
from datetime import timedelta, datetime
import re
import sqlite3
import os
from uptime import uptime

# --- Database configuration ---
DATABASE = os.path.join(os.getcwd(), 'sslExpiry.db')
DB_SCHEMA = os.path.join(os.getcwd(), 'schema.sql')

# --- Database operations ---


def get_db(database: str):
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(database: str, database_schema: str):
    with get_db(database) as conn:
        cursor = conn.cursor()

        with open(database_schema, mode='r') as f:
            cursor.executescript(f.read())
            f.close()
            conn.commit()


def ServerUptime():
    t = uptime()

    # create timedelta and convert it into string
    td_str = str(timedelta(seconds=t))

    # split string into individual component, to be Human Readable
    x = td_str.split(':')
    uptimehr = x[0] + ' Hours, ' + x[1] + ' Minutes'
    return uptimehr


def getHostnameCount(database: str) -> int:
    """
    input: path to database
    output : integer with the distinct count of hostnames in DB
    """
    with get_db(database) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
                SELECT COUNT(DISTINCT hostname) AS "Hostname_Count"
                FROM certificate_checks;
            """
        )
    try:
        counthostname, = cursor.fetchone()
    except Exception:
        counthostname = 0
    cursor.close()
    conn.close()
    return counthostname


def getLastHostname(database) -> str:
    """
    input: path to database
    output : str with the last fqdn checked
    """
    with get_db(database) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT hostname
            FROM certificate_checks
            ORDER BY check_date DESC LIMIT 1;
            """
        )
    try:
        fqdn, = cursor.fetchone()
    except Exception:
        fqdn = "Error"
    cursor.close()
    conn.close()
    return fqdn


def getLastHourChecks(database) -> int:
    """
    input: path to database
    output : count of checks within last hour (integer)
    """

    # Last hour checks
    current_time = datetime.now()
    lasthour = current_time.timestamp() - 3600

    count_last_hour = f"""
        SELECT COUNT(DISTINCT hostname) AS "LastHourCount"
        FROM certificate_checks
        WHERE check_date >= {lasthour};
        """

    with get_db(database) as conn:
        cursor = conn.cursor()
        cursor.execute(count_last_hour)
    try:
        count_last_hour, = cursor.fetchone()
    except Exception:
        count_last_hour = -1
    cursor.close()
    conn.close()
    return count_last_hour


def get_stats():
    """
    Execute some queries and returns a dict like:
    {
        "Hostname Count": 124,
        "Last Hostname": "sc-activation.bachmann.info",
        "Last Hour Checks": 7,
        "Server Uptime": "164 days, 2 Hours, 14 Minutes"
    }
    """
    theStats = {}
    theStats["Hostname Count"] = getHostnameCount(DATABASE)
    theStats["Last Hostname"] = getLastHostname(DATABASE)
    theStats["Last Hour Checks"] = getLastHourChecks(DATABASE)
    theStats["Server Uptime"] = ServerUptime()
    return jsonify(theStats)

# --- Class definitions


@dataclass
class CertificateCheckRequest:
    """
    This data class represents a hostname and TCP port
    It is used to validate the params.
    """
    hostname: str
    port: int = 443

    def __post_init__(self):
        if not self.port or not isinstance(self.port, int):
            raise ValueError(f"""Port must be a non-empty integer, got {self.port}.""")

        if not (1 <= self.port <= 65535):
            raise ValueError(f"""Port number must be an integer between 1 and 65535, got {self.port}.""")

        if not self.hostname or not isinstance(self.hostname, str):
            raise ValueError(f"""Hostname must be a non-empty string, got '{self.hostname}'.""")

        self.hostname = self.hostname.strip().lower()

        # Remove whitespace and trailing slash if present.
        self.hostname = self.hostname.strip().rstrip('/')

        # Remove the "https://" prefix if present
        if self.hostname.startswith('https://'):
            self.hostname = self.hostname[8:]

        """
        Defined the regular expression pattern for a FQDN
        with great help of https://regex-generator.olafneumann.org/
        To implement https://yozachar.github.io/pyvalidators/stable/api/hostname/
        """
        # Find FQDN in the test string
        pattern = r"^(?!-)(?:[a-z0-9]+(?:-+[a-z0-9]+)*\.)+[a-z0-9]+(?:-+[a-z0-9]+)*(?<!-)$"
        match = re.match(pattern, self.hostname)

        if match:
            return match.group(0)
        else:
            raise ValueError("Hostname must be a valid FQDN.")


@dataclass
class LametricResponse:
    """
    Build the response, in accordance to Lametric's requirements
    """
    frames: dict = field(default_factory=dict)

    def __post_init__(self) -> dict:
        self.frames = {
                "frames": [
                            {
                            "text": "SSL exp",
                            "icon": "i133"
                            }
                          ]
                }
        return self.frames

    def add_frame(self, text: str, icon: str):
        frame = {
                    "text": text,
                    "icon": icon
                }

        self.frames['frames'].append(frame)
        return self.frames


def check_ssl_certificate(hostname: str, port: int):
    """
    Create a connection and get the exiry date.
    Compute the remaining number of days.
    Returns 3 values:
        * is_valid
        * remaining_days
        * error_message
    """
    context = ssl.create_default_context()

    try:
        with socket.create_connection((hostname, port), timeout=5) as sock:
            with context.wrap_socket(sock,
                                     server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

                # Find expiration date
                exp_date = cert['notAfter']

                expiry = datetime.strptime(exp_date, '%b %d %X %Y %Z')
                today = datetime.today()
                delta = expiry - today

                return True, delta.days, None

    except OSError:
        return False, 0, "No Info"
    except socket.timeout:
        return False, 0, "Timeout"
    except ConnectionRefusedError:
        return False, 0, "Sever refused connection"
    except ssl.SSLError as e:
        return False, 0, f"SSL Error: {e}"
    except Exception as e:
        return False, 0, f"Unattended Error: {e}"


# Init Flask application
ssl_expiry_app = Flask(__name__)

# Ensure DB is correctly inialized at app startup
with ssl_expiry_app.app_context():
    init_db(DATABASE, DB_SCHEMA)

# Flask Routes


@ssl_expiry_app.route("/api/v1", methods=['GET'])
def check_certificate():
    raw_hostname = request.args.get("hostname", type=str)
    raw_port = request.args.get("port", -1, type=int)

    try:
        # Validate inputs using a dataclass
        req_params = CertificateCheckRequest(hostname=raw_hostname,
                                             port=raw_port)

        # Check Certificate expiry
        is_valid, days_remaining, error_message = check_ssl_certificate(req_params.hostname, req_params.port)

        # Store data in DB
        with get_db(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO certificate_checks (
                    hostname,
                    port,
                    is_valid,
                    days_remaining,
                    error_message)
                VALUES (?, ?, ?, ?, ?)
                """,
                (req_params.hostname,
                 req_params.port,
                 is_valid,
                 days_remaining,
                 error_message)
            )
            conn.commit()

        # Prepare Lametric answers (frames)
        lametric_response = LametricResponse()

        if is_valid:
            if days_remaining >= 0:
                lametric_response.add_frame(text=f"{days_remaining} days", icon="a464")
            else:
                lametric_response.add_frame(text="Expired!", icon="i4672")
        else:
            lametric_response.add_frame(text=f"{error_message}", icon="i4672")

        return jsonify(lametric_response.frames)

    except ValueError as e:
        # Erreur de validation (champs vides, format incorrect, etc.)
        lametric_response = LametricResponse()
        lametric_response.add_frame(text=f"Erreur: {e}", icon="i4672")
        return jsonify(lametric_response.frames), 400  # Bad Request
    except TypeError as e:
        # Erreur de type (par exemple, port non numérique)
        lametric_response = LametricResponse()
        lametric_response.add_frame(text=f"Erreur: {e}", icon="i4672")
        return jsonify(lametric_response.frames), 400  # Bad Request
    except Exception as e:
        # Erreur interne du serveur
        lametric_response = LametricResponse()
        lametric_response.add_frame(text="Internal Error", icon="i4672")
        lametric_response.add_frame(text=f"Detail: {e}", icon="i4672")
        return jsonify(lametric_response.frames), 500  # Internal Server Error


@ssl_expiry_app.route("/", methods=['GET'])
def webFrontEnd():
    return render_template('index.html')


@ssl_expiry_app.route("/api/v1/metrics", methods=['GET'])
def statistics():
    return get_stats()


# Testing to check if it works
@ssl_expiry_app.route('/test')
def test():
    """
    Tests to implement
    """
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
