"""
    Interpreter: Python 3.6
"""
import http.server
import socketserver
from urllib.parse import urlparse
from http import HTTPStatus
from datetime import date, datetime
import pymysql
import pymysql.cursors
import json

def db_open_kiwi():
    # Connect to the database
    connection = pymysql.connect(host='localhost',
                                 user='kiwi_user',
                                 password='pss73549189w',
                                 db='kiwi_task',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
    print("db_open_kiwi:   connection OPENED")
    return connection


def db_close_kiwi(connection):
    connection.close()
    print("db_close_kiwi:   connection CLOSED")


def db_modify_data(username, birth_date_str, connection):
    with connection.cursor() as cursor:
        print("db_modify_data:   entered")
        sql = "INSERT INTO `user_data` (`username`, `birth_date_str`) VALUES (%s,%s) ON DUPLICATE KEY UPDATE birth_date_str=%s"
        cursor.execute(sql, (username, birth_date_str, birth_date_str))
        print("db_modify_data:   " + str((sql, (username, birth_date_str, birth_date_str))))
    connection.commit()


def db_select_data(username, connection):
    with connection.cursor() as cursor:
        # Read a single record
        sql = "SELECT `birth_date_str` FROM `user_data` WHERE `username` =%s"
        cursor.execute(sql, username)
        birth_date_dict = cursor.fetchone()
        # Example: birth_date_dict= {'birth_date_str': '1984-03-17'}   it's a dictionary
        birth_date_str = birth_date_dict['birth_date_str']

        print("db_select_data:   birth_date_str= " + str(birth_date_str))

    return birth_date_str


def srv_run():
    port = 8180
    handler = ExtendedHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)
    print("serving at port", port)
    httpd.serve_forever()


def get_days_to_bday(birth_date_str):
    # TODO: dates validation.
    # TODO: Feb29th workaround.
    curr_date_str = datetime.strftime(date.today(), '%Y-%m-%d')
    curr_date = datetime.strptime(curr_date_str, '%Y-%m-%d')
    print("get_days_to_bday:   curr_date: " + str(curr_date))

    birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d')
    print("get_days_to_bday:   birth_date: " + str(birth_date))

    this_year_bdate = datetime(curr_date.year, birth_date.month, birth_date.day)
    print("get_days_to_bday:   this year b-day: " + str(this_year_bdate))
    next_year_bdate = datetime(curr_date.year + 1, birth_date.month, birth_date.day)
    print("get_days_to_bday:   next year b-day: " + str(next_year_bdate))

    if curr_date > this_year_bdate:
        days_to_bday = (next_year_bdate - curr_date).days
    else:
        days_to_bday = (this_year_bdate - curr_date).days
    print("get_days_to_bday:   days_to_bday: " + str(days_to_bday))
    return days_to_bday


def http_construct_body(username, days_untill_bday):
    if days_untill_bday > 0:
        message = "Hello, " + str(username) + "! Your birthday is in " + str(days_untill_bday) + " day(s)"
    else:
        message = "Hello, " + str(username) + "! Happy birthday!"
    print("http_construct_body:   message: " + str(message))
    return message


class ExtendedHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    # This class extends the SimpleHTTPRequestHandler class from the http.server module.
    # Warning! http.server is not recommended for production. It only implements basic security checks.

    def http_send_reply(self, message):
        print("http_send_reply:   body: " + str(message))
        body = message.encode('UTF-8', 'replace')
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "application/json")
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_PUT(self):
        """
        Saves/updates given user's name and birthdate to database:
        Request: PUT /hello/<username> {"dateOfBirth": "YYYY-MM-DD"}
        curl -v -X PUT -H "Content-Type: application/json" -d '{"dateOfBirth": "1999-03-03"}' localhost:8889/hello/sman

        Response: 204 No Content
        Rules:
            - username must contain only letters;
            - date must be before current date
        """
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

        print("do_PUT:   Path: " + str(self.path))
        print("do_PUT:   ---headers--- \n" + str(self.headers))

        path_split = self.path.split("/", 2)
        username = path_split[-1]
        print("do_PUT:   username: " + str(path_split[-1]))  # nikolay/uuuuer
        length = int(self.headers["Content-Length"])
        ''' 
        I assume that the following structure is sent as a payload: {"dateOfBirth": "1999-03-03"} (JSON, double quotes)
        '''
        bytes_payload = self.rfile.read(length)
        payload_str = bytes_payload.decode("utf-8")  # that's a string: {"dateOfBirth": "1999-03-03"}
        payload_list = payload_str.split("\"")  # that's a list: ['{', 'dateOfBirth', ': ', '1999-03-03', '}']
        birth_date_str = payload_list[3]  # that's a 1999-03-03

        print("do_PUT:   birth_date_str: " + str(birth_date_str))

        # TODO: date validation.
        curr_date_str = datetime.strftime(date.today(), '%Y-%m-%d')
        curr_date = datetime.strptime(curr_date_str, '%Y-%m-%d')
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d')

        if curr_date >= birth_date:
            connection = db_open_kiwi()
            db_modify_data(username, birth_date_str, connection)
            print("do_PUT:   new data is sent to db!")
            db_close_kiwi(connection)
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
        path_split = self.path.split("/", 2)
        print("do_GET:   path_split: " + str(path_split))  # ['', 'hello', 'nikolay/uuuuer']
        username = path_split[-1]
        print("do_GET:   username: " + str(path_split[-1]))  # nikolay/uuuuer
        print("do_GET:   Let's open db_conn")
        connection = db_open_kiwi()
        print("do_GET:   opened!")
        birth_date_str = db_select_data(username, connection)
        db_close_kiwi(connection)

        days_until_bday = get_days_to_bday(birth_date_str)
        message = http_construct_body(username, days_until_bday)

        self.http_send_reply(message)
        print("do_GET:   DONE! \n")


if __name__ == '__main__':
    print("Let's start web-server\n")
    srv_run()
