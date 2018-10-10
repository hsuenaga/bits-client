#!/usr/bin/env python3

import sys
import ssl
import urllib.request
import json
import pprint

class BitsRestClient:
    url_base = ''

    api_auth = 'api/base/auth/signin'
    api_modules = 'api/base/modules'
    api_omgs = 'api/base/omgs'
    api_users = 'api/base/users'
    api_discovery = 'api/bits-devices/devices'
    api_camera = 'api/camera-manager/cameras'
    api_sensors = 'api/sensors/devices'

    headers = {}
    headers["Accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    headers["Authorization"] = ""

    authenticated = False
    
    def auth(self, userid = None, userpass = None):
        self.headers.pop("Authorization", None)

        send = {}
        if userid is None:
            send["type"] = "anonymous"
        else:
            send["type"] = "username"
            send["username"] = userid
            send["password"] = userpass

        recv = self.req_post(self.api_auth, send)
        if recv is None:
            authenticated = False
            return None
        auth_obj = 'Bearer ' + recv['token']
        self.headers["Authorization"] = auth_obj
        authenticated = True
        return recv['token']

    def modules(self, unit=None):
        recv = self.req_get(self.api_modules, unit)
        return recv

    def omgs(self, unit=None):
        recv = self.req_get(self.api_omgs, unit)
        return recv

    def users(self, unit=None):
        recv = self.req_get(self.api_users, unit)
        return recv

    def discovery(self, unit=None):
        recv = self.req_get(self.api_discovery, unit)
        return recv

    def cameras(self, unit=None):
        recv = self.req_get(self.api_camera, unit)
        return recv

    def sensors(self, unit=None):
        recv = self.req_get(self.api_sensors, unit)
        return recv

    ## private
    def req_get(self, api, unit):
        url = self.url_base + api
        if unit is not None:
            url = url + '/' + unit
        print("GET URL: " + url)
        req = urllib.request.Request(url, method="GET", headers=self.headers)
        return self.do_req(req)

    def req_post(self, api, data):
        url = self.url_base + api
        json_data = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, method="POST", data=json_data, headers=self.headers)
        return self.do_req(req)

    def do_req(self, req):
        try:
            with urllib.request.urlopen(req) as res:
                body = res.read().decode("utf-8")
                data = json.loads(body)
        except urllib.error.HTTPError as e:
            print("HTTP Error: ", e)
            data = None
        return data

##
## Simple Test
##

# don't verify self-signed certificate
ssl._create_default_https_context = ssl._create_unverified_context

bits = BitsRestClient()
bits.url_base = 'https://192.168.0.242/'

print('Try Authentication')
token = bits.auth("bits-user", "bits-passwd")
if token is None:
    print('Warning: authentication failed.')

args = sys.argv
if len(args) <= 1:
    args = ['all']

for target in args:
    if target in {'module', 'modules', 'all'}:
        print('Available Modules:')
        modules = bits.modules()
        pprint.pprint(modules)

    if target in {'omg', 'omgs', 'all'}:
        print('Available OMG:')
        omgs = bits.omgs()
        pprint.pprint(omgs)

    if target in {'user', 'users', 'all'}:
        print('Available Users:')
        users = bits.users()
        pprint.pprint(users)

    if target in {'node', 'nodes', 'all'}:
        print('Bits Nodes:')
        nodes = bits.discovery()
        pprint.pprint(nodes)

    if target in {'camera', 'cameras', 'all'}:
        print('Bits Cameras:')
        cameras = bits.cameras()
        pprint.pprint(cameras)

    if target in {'sensor', 'sensors', 'all'}:
        print('Bits Sensors:')
        sensors = bits.sensors()
        pprint.pprint(sensors)
        print('Bits Sensors by Id:')
        sensor_list = sensors['result']
        for dev in sensor_list:
            unit_id = dev['id']
            print('Access Device: ' + unit_id)
            unit = bits.sensors(unit_id)
            pprint.pprint(unit)
            print('Access Device: ' + ':' + unit_id)
            unit = bits.sensors(':' + unit_id)
            pprint.pprint(unit)
