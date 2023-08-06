# ksalf   

[![PyPI](https://img.shields.io/pypi/v/ksalf.svg)](https://pypi.org/project/ksalf/)   

A lightweight experimental HTTP handler inspired by flask.   
**! This is just a experimental (fun) project, please don't use it in production !**

## Implemtation
Ksalf is a lightweight handler for the [python (base) http server](https://docs.python.org/3/library/http.server.html)   .    
It provides new feature like **URL parsing and HTML responses**, to the python in-build http server.  
Ksalf currently only supports **GET** requests.    
The project was inspired by the [flask python project](https://github.com/pallets/flask).

## Installtion
```
pip install ksalf
```

## Example
```
from http.server import HTTPServer
from ksalf import HTTPHandler

class Handler(HTTPHandler):

    @HTTPHandler.route("/health")
    def GET(self):
        self.respond(b'healthy')

if __name__ == "__main__":
    PORT = 8080
    httpd = HTTPServer(('0.0.0.0', PORT), Handler)
    print("Server running on http://localhost:" + str(PORT))
    httpd.serve_forever()
```

This example would serve a simple web app on your localhost:8080.  
You can register a route with @HTTPHandler.route("/<your_route>").  
*GET* requests always get processed by the `def GET(self):` implementation.   
**curl**
```
curl localhost:8080/health
```
**Response**
```
healthy
```


## Future Development
* Implement tests
* Support other request methods than just *GET*
* Advanced URL parsing
* Enhance HTML Responses
