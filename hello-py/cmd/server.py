"""
    Interpreter: Python 3.6
"""

import http.server
import socketserver
from http import HTTPStatus
from datetime import date, datetime
import pymysql
import pymysql.cursors
import json
import os


def db_open():
    # user/password are assigned via ENV_VARS through K8s secret.
    # host/db assigned via K8s ConfigMap.
    connection = pymysql.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        db=os.environ['DB'],
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor)
    print("db_open:   connection OPENED")
    return connection


def db_close(connection):
    connection.close()
    print("db_close:   connection CLOSED")


def db_update(username, birth_date, connection):
    with connection.cursor() as cursor:
        print("db_update:   entered")
        sql = "INSERT INTO `user_data_date` (`username`, `birth_date`) VALUES (%s,%s) ON DUPLICATE KEY UPDATE birth_date=%s"
        cursor.execute(sql, (username, birth_date, birth_date))
        print("db_update:   " + str((sql, (username, birth_date, birth_date))))
    connection.commit()


def db_select(username, connection):
    with connection.cursor() as cursor:
        # Read a single record
        sql = "SELECT `birth_date` FROM `user_data_date` WHERE `username` =%s"
        cursor.execute(sql, username)
        birth_date_dict = cursor.fetchone()
        # Example: birth_date = {'birth_date': '1984-03-17'}   it's a dictionary
        birth_date = birth_date_dict['birth_date']

        print("db_select:   birth_date = " + str(birth_date))

    return birth_date


def srv_run():
    # port = 8181
    # port value provided via k8s ConfigMap
    port = os.environ['LISTEN_PORT']
    handler = ExtendedHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)
    print("serving at port", port)
    httpd.serve_forever()


def get_days_to_bday(birth_date):
    # TODO: Add date validation to prevent usage of non-existing dates (Ex. Mar-136th).
    # TODO: Add logic to calculate days_to_bday if birthday is on Feb 29th.

    curr_date = date.today()

    this_year_bdate = date(curr_date.year, birth_date.month, birth_date.day)
    next_year_bdate = date(curr_date.year + 1, birth_date.month, birth_date.day)

    if curr_date > this_year_bdate:
        days_to_bday = (next_year_bdate - curr_date).days
    else:
        days_to_bday = (this_year_bdate - curr_date).days
    print("get_days_to_bday:   days_to_bday: " + str(days_to_bday))
    return days_to_bday


def http_construct_json(username, days_to_bday):
    if days_to_bday > 0:
        message = "Hello, " + str(username) + "! Your birthday is in " + str(days_to_bday) + " day(s)"
    else:
        message = "Hello, " + str(username) + "! Happy birthday!"
    message_dict = {"message": message}
    json_obj = json.dumps(message_dict)
    print("http_construct_json:   message: " + str(message_dict))
    return json_obj


class ExtendedHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    # This class extends the SimpleHTTPRequestHandler class from the http.server module.
    # Warning! http.server is not recommended for production. It only implements basic security checks.

    def http_send_reply(self, json_obj):
        print("http_send_reply:   json_obj: " + str(json_obj))
        json_encoded = json_obj.encode('UTF-8', 'replace')
        content = bytearray(json_encoded)

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_PUT(self):
        """
        Saves/updates given user's name and birthdate to database:
        Request: PUT /hello/<username> {"dateOfBirth": "YYYY-MM-DD"}
        I assume that the following structure is sent as a payload: {"dateOfBirth": "1999-03-03"} (JSON, double quotes)
        curl -v -X PUT -H "Content-Type: application/json" -d '{"dateOfBirth": "1999-03-03"}' localhost:8889/hello/sman

        Response: 204 No Content
        Rules:
            - username must contain only letters;
            - date must be before current date
        """
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

        path_split = self.path.split("/", 2)
        username = path_split[-1]
        length = int(self.headers["Content-Length"])
        bytes_payload = self.rfile.read(length)

        # TODO: validate if we've got a valid JSON from client.
        json_obj = json.loads(bytes_payload)
        # TODO: check if there is a 'dateOfBirth' field in that JSON.
        birth_date_str = json_obj['dateOfBirth']  # that's a 1999-03-03
        # TODO: check if the value for 'dateOfBirth' is a string.
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d')
        birth_date = birth_date.date()
        print("do_PUT:   birth_date: " + str(birth_date))

        curr_date = date.today()

        if curr_date >= birth_date:
            connection = db_open()
            db_update(username, birth_date, connection)
            print("do_PUT:   new data is sent to db!")
            db_close(connection)
            print("do_PUT:   DONE! \n")
        else:
            print("do_PUT:   The birth_date is in the future. Not saving to DB.\n")

    def do_GET(self):
        """
        Returns hello birthday message for given user
            Request: GET /hello/<username>
            Response: 200 OK
        """
        print("do_GET:   got: " + str(self.path))
        path_split = self.path.split("/", 2)  # ['', 'hello', 'nikolay/uuuuer']
        username = path_split[-1]  # nikolay/uuuuer
        print("do_GET:   Let's open db_conn")
        connection = db_open()
        birth_date = db_select(username, connection)
        db_close(connection)

        days_until_bday = get_days_to_bday(birth_date)
        json_obj = http_construct_json(username, days_until_bday)

        self.http_send_reply(json_obj)
        print("do_GET:   DONE! \n")


if __name__ == '__main__':
    # TODO: logging.
    print("Let's start web-server\n")
    srv_run()
