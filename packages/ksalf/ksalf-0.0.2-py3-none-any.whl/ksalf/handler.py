from http.server import BaseHTTPRequestHandler
from http import HTTPStatus
from os import curdir, sep
import re


class HTTPHandler(BaseHTTPRequestHandler):
    endpoints = {}

    def route(route_path="/"):
        """
        Register a GET route for the handler.

        Keyword Arguments:
        route_path: request route -> string (default: "/")
        """
        def decorate(func):
            # Gets called on init
            # Registers a function for the given route.
            arguments = func.__code__.co_varnames[:func.__code__.co_argcount]
            HTTPHandler.endpoints[route_path] = func

            def call(self, *args, **kwargs):
                # Gets called when the function gets called
                # Returns method, which is associated with the requests route
                if self.request_path in self.endpoints:
                    result = self.endpoints[self.request_path](self, *args, **kwargs)
                elif self.request_path.endswith(".css"):
                    f = open(curdir + sep + self.request_path)
                    self.respond(f.read().encode(), "text/css")
                    f.close()
                    return
                else:
                    return
                return result
            return call
        return decorate

    def do_GET(self):
        """
        Call on a GET request and parses the url paramters of the request.

        It then calls the GET() method.
        """
        self.parameters = self.__parse_request()
        self.request_path = self.parameters.get("path")
        self.GET()

    def __parse_request(self):
        """
        Parse the arguements(after the ?) in the url.

        Example:
        localhost:8080?name=peter&year=2020
        paramter["name"] = "peter"
        paramter["year"] = "2020"

        Return:
        parameters: paramters in the url -> dict
        """
        parameters = {}
        splitted_path = self.path.split("?")
        parameters["path"] = splitted_path[0]
        params = re.findall(r"[\w']+", ' '.join(map(str, splitted_path[1:])))
        if len(params) % 2:
            params.pop()
        if len(params) > 1:
            for i in range(0, len(params), 2):
                parameters[params[i]] = params[i+1]
        return parameters

    def respond(self, response_blob, mimetype="text/html"):
        """
        Create a http response.

        Keyword arguments:
        response_blob: content -> bytes
        mimetype: Return type, please specify -> string (default: text/plain)
        """
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', mimetype)
        self.end_headers()
        self.wfile.write(response_blob)
        return

    def GET(self):
        """
        Automatically called on GET request.

        Override with own implementation.
        """
        pass
