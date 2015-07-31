from wsgiref.simple_server import make_server

def application(environ, start_response):
    """Main WSGI entry point"""
    value = ""
    url = environ['PATH_INFO'].split('/')
    if len(url) == 2 and url[1] == '':
        name = ""
    else:
        name = ' '.join(url[1:])
        
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return "Hello %s !" % (name)

if __name__=='__main__':
    httpd = make_server('', 8080, application)
    print("Serving on port 8080...")
    httpd.serve_forever()
