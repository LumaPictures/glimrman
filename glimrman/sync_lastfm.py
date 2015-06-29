#!/usr/bin/env python
import os
import logging
from pprint import pprint

import requests
import pylast
import sqlalchemy
from sqlalchemy.orm import sessionmaker

from .models import *

log = logging.getLogger(__name__)


def main():
    API_KEY = "8cf94278fd43cdf00c3fc3b76c8d6ff5"
    API_SECRET = "be6402530c1b814bc62bd2fbec05a4caq"

    username = "lumapictures"
    # password_hash = pylast.md5("321lumatunes!")

    r = requests.get('http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=%s&format=json' % (username, API_KEY))
    if 199 < r.status_code < 300:
        pprint(r.json())
    else:
        print 'error %d' % r.status_code

    # network = pylast.LastFMNetwork(api_key=API_KEY, 
    #                                api_secret=API_SECRET, 
    #                                username=username,
    #                                password_hash=password_hash)

    # # now you can use that object every where
    # artist = network.get_artist("System of a Down")
    # artist.shout("<3")

    # track = network.get_track("Iron Maiden", "The Nomad")
    # track.love()
    # track.add_tags(("awesome", "favorite"))

    # type help(pylast.LastFMNetwork) or help(pylast) in a python interpreter to get more help
    # about anything and see examples of how it works


if __name__ == '__main__':
    main()
