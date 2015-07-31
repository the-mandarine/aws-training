from wsgiref.simple_server import make_server
from boto import dynamodb2
from boto.dynamodb2.table import Table
from boto.dynamodb2.items import Item
from boto.dynamodb2.exceptions import ConditionalCheckFailedException
from jinja2 import Environment, FileSystemLoader
from cgi import FieldStorage
from time import time
import os

DYDB_CONN = dynamodb2.connect_to_region(os.environ['AWS_REGION'])
DYDB_TABLE = Table(table_name=os.environ['DYDB_TABLENAME'], connection=DYDB_CONN)

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
J2_ENV = Environment(loader=FileSystemLoader(CUR_DIR), trim_blocks=True)
PAGE_TPL = J2_ENV.get_template('template.html')


def dydb_store(data):
    try:
        item = Item(DYDB_TABLE, data=data)
        item.save()
    except ConditionalCheckFailedException:
        pass

def dydb_retrieve():
    msgs = []
    msg_iter = DYDB_TABLE.scan()
    for msg in msg_iter:
        msgs.append({'timestamp': msg['timestamp'], 
                     'name': msg['name'], 
                     'message': msg['message']})
    sorted_msgs = sorted(msgs, key=lambda msg: msg['timestamp'])
    return sorted_msgs

def application(environ, start_response):
    """Main WSGI entry point"""
    
    if environ['REQUEST_METHOD'] == 'POST':
        post_env = environ.copy()
        post_env['QUERY_STRING'] = ''
        fields = FieldStorage(fp=environ['wsgi.input'],
                              environ=post_env,
                              keep_blank_values=True)
        name = fields['name'].value
        message = fields['message'].value
        timestamp = time()
        data = {'timestamp': timestamp, 'name': name, 'message': message}
        dydb_store(data)
        start_response('301 Redirect', 
                       [('Content-Type', 'text/html'), ('Location', '/')])
        return ''
    elif environ['REQUEST_METHOD'] == 'GET':
        msgs = dydb_retrieve()
        start_response('200 OK', [('Content-Type', 'text/html')])
        return str(PAGE_TPL.render(msgs=msgs))

if __name__=='__main__':
    httpd = make_server('', 8080, application)
    print("Serving on port 8080...")
    httpd.serve_forever()
