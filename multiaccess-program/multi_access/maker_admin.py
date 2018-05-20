import json
from collections import namedtuple
from os.path import join
from tempfile import gettempdir

import requests

from multi_access.util import dt_parse

MakerAdminMember = namedtuple('MakerAdminMember', [
    'member_id',      # int for debugging
    'member_number',  # int
    'firstname',      # string
    'lastname',       # string
    'key_id',         # int for debugging
    'rfid_tag',       # string
    'blocked',        # bool
    'end_timestamp',  # string timestamp in zulu
])


class MakerAdminClient(object):
    
    def __init__(self, ui=None, base_url=None, members_filename=None):
        self.ui = ui
        self.base_url = base_url
        self.members_filename = members_filename
        self.token = 'nokey'
        self.tokenfile = join(gettempdir(), 'LFP7EL5K6SFF.TXT')
        try:
            with open(self.tokenfile) as r:
                self.token = r.read().strip()
        except OSError:
            pass
        
    def login(self):
        username, password = self.ui.promt__login()
        r = requests.post(self.base_url + "/oauth/token",
                          {"grant_type": "password", "username": username, "password": password})
        
        if not r.ok:
            return
        self.token = r.json()["access_token"]
        with open(self.tokenfile, 'w') as w:
            w.write(self.token)
    
    def get_and_login_if_needed(self, url):
        for i in range(3):
            r = requests.get(url, headers={'Authorization': 'Bearer ' + self.token})
            if r.ok:
                return r.json()
            elif r.status_code == 401:
                self.login()
            else:
                self.ui.fatal__error(f"failed to get data, got ({r.status_code}):\n" + r.text)
        else:
            self.ui.fatal__error("failed to login")

    def fetch_members(self, ui):
        """ Fetch and return list of MakerAdminMember, raises exception on error. """
        if self.members_filename:
            ui.info__progress(f"getting members from file {self.members_filename}")
            with open(self.members_filename) as f:
                data = json.load(f)
        else:
            url = self.base_url + '/multiaccess/memberdata'
            ui.info__progress(f"getting members from {url}")
            data = self.get_and_login_if_needed(url)['data']

        for m in data:
            m['end_timestamp'] = dt_parse(m['end_timestamp'])
            
        res = [MakerAdminMember(**m) for m in data]

        ui.info__progress(f"got {len(res)} members")

        return res
