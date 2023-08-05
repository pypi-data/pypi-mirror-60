import getpass
import os
import sys
import unittest
import uuid
from datetime import datetime
from pathlib import Path

from inmation_api_client.inclient import Client
from inmation_api_client.model import Item, Identity
from inmation_api_client.options import Options

p = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent
sys.path.append(str(p))
sys.path.append(str(Path(p).parent))

AUTH = {
    'auth': {
        'username': 'username',
        'password': 'password',
    }
}

_username = _password = ''
_host = None
_port = None

if os.path.isfile(os.path.join(p, '.env')):
    with open(os.path.join(p, '.env')) as fr:
        _username = fr.readline().strip()
        _password = fr.readline().strip()
        _host = fr.readline().strip()
        _port = fr.readline().strip()

AUTH['auth']['username'] = _username if _username else input('inmation Profile Username:')
AUTH['auth']['password'] = _password if _password else getpass.getpass('inmation Profile Password:')

OPTIONS = Options(AUTH)
client = Client()
# client.EnableDebug()
opt = OPTIONS


def setup():
    client.Connect(host=_host or '127.0.0.1', port=_port or 8002, options=opt)

    response = client.RunScript(Identity('/System'), 'return inmation.getcorepath()')

    if response is None:
        sys.exit('Connection failed. Unable to get the core path')
    if 'data' not in response.keys():
        sys.exit('The RunScript property of the WebAPIServer object under the Server model is probably disabled, enable it and try again.')
    else:
        core_path = response['data'][0]['v']
    return core_path


CORE_PATH = setup()


def create_folder():
    f_name = 'PythonTestFolder ' + str(uuid.uuid4())
    f_path = CORE_PATH + '/' + f_name

    client.Mass([
        {
            'path': f_path,
            'operation': 'UPSERT',
            'class': 'GenFolder',
            'ObjectName': f_name
        }
    ])
    return f_path


class TestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = client
        cls.opt = opt
        cls.path = create_folder()
        cls.core_path = CORE_PATH

    def connect(self):
        self.client.Connect(options=self.opt)

    def run_coro(self, coro):
        return self.client.GetEventLoop().run_until_complete(coro)

    @classmethod
    def tearDownClass(cls):
        cls.client.Mass([
            {
                'path': cls.path,
                'operation': 'REMOVE',
                'class': 'GenFolder',
                'ObjectName': cls.path.split('/')[-1]
            }
        ])
