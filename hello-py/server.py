"""
    Interpreter: Python 3.6

    The below code extends the SimpleHTTPRequestHandler class from the http.server module.
    Additionally I've been using:
        https://docs.python.org/3.6/library/http.server.html
        https://gist.github.com/fabiand/5628006
        https://stackoverflow.com/questions/25316046/parsing-get-request-data-with-from-simplehttpserver
        https://docs.python.org/3/library/urllib.parse.html
        https://www.w3schools.com/python/ref_string_split.asp :-)
"""
import http.server
import socketserver
from urllib.parse import urlparse
from http import HTTPStatus
from datetime import date, datetime
import json


birth_date_str = '1984-08-10'

def srv_run():
    PORT = 8888
    handler = SputHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    print("serving at port", PORT)
    httpd.serve_forever()


def calculate_dates(birth_date, curr_date):
    this_year_bdate = datetime(curr_date.year, birth_date.month, birth_date.day)
    print("this year b-day: "+ str(this_year_bdate))
    next_year_bdate = datetime(curr_date.year+1, birth_date.month, birth_date.day)
    print("next year b-day: "+ str(next_year_bdate ))
    if curr_date > this_year_bdate:
        days_untill_bday = (next_year_bdate - curr_date).days
    else:
        days_untill_bday = (this_year_bdate - curr_date).days

    return days_untill_bday

#curr_date = date.today()
curr_date_str = datetime.strftime(date.today(), '%Y-%m-%d')
curr_date = datetime.strptime(curr_date_str, '%Y-%m-%d')
print("curr_date: " + str(curr_date))

birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d')
print("birth_date: " + str(birth_date))

days_untill_bday = calculate_dates(birth_date, curr_date)

"""
            A. if username's birthday is in N days:
                { "message": "Hello, <username>! Your birthday is in N day(s)" }
            B. if username's birthday is today:
                { "message": "Hello, <username>! Happy birthday!" }
"""

print("+++")
if days_untill_bday > 0:
    print("Hello, <username>! Your birthday is in " + str(days_untill_bday) + " day(s)")
else:
    print("Hello, <username>! Happy birthday!")



#Handler = http.server.SimpleHTTPRequestHandler
#Handler = http.server.BaseHTTPRequestHandler

class SputHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    from urllib.parse import urlparse
    def send_reply(self, srv_reply):
        #message = name
        print("sendHead: "+str(srv_reply))

        self.send_response(HTTPStatus.OK)
        #self.send_response(201, " DONE ")

        #self.send_header("Content-type", "html/text")
        #self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        #self.end_headers()
        #self.send_response(201, " DONE ")

        #body = None


        body = srv_reply.encode('UTF-8', 'replace')
        self.send_header("Content-type", "text/html")
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


    def do_PUT(self):
        """
        Saves/updates given user's name and birthdate to database:
        Request: PUT /hello/<username> {"dateOfBirth": "YYYY-MM-DD"}
        Response: 204 No Content
        Rules:
            - username must contain only letters;
            - date must be before current date
        """
        self.send_response(204, "No Content")
        self.end_headers()

        print("Headers: ")
        print(self.headers)
        print("Path: "+str(self.path))
        length = int(self.headers["Content-Length"])
#        path = self.translate_path(self.path)
#        with open(path, "wb") as dst:
#            dst.write(self.rfile.read(length))
        bytes = self.rfile.read(length)
        string = bytes.decode("utf-8")
        print(string)

    def do_GET(self):
        """
        Returns hello birthday message for given user
            Request: GET /hello/<username>
            Response: 200 OK
        """
        bits = urlparse(self.path)
        #print(self.path)        # /hello/nikolay/uuuuer
        username = self.path.split("/", 2)
        print("got_username: "+str(username))              #  ['', 'hello', 'nikolay/uuuuer']
        print("transformed: "+str(username[-1]))          #  nikolay/uuuuer
        username = username[-1]
        #print(name, self.path, self.command, self.request_version, bits.scheme, bits.netloc,
         #                bits.path, bits.params, bits.query, bits.fragment,
         #                bits.username, bits.password, bits.hostname, bits.port)
        """
        payload Examples:
            A. if username's birthday is in N days:
                { "message": "Hello, <username>! Your birthday is in N day(s)" }
            B. if username's birthday is today:
                { "message": "Hello, <username>! Happy birthday!" }
        """

        srv_response = username

        #self.send_response(HTTPStatus.OK)
        self.send_reply(srv_response)
#        self.send_header("Content-type", ctype)


# TODO: check how SimpleHTTPRequestHandler.do_GET is done.

if __name__ == '__main__':
    srv_run()
    print("22")