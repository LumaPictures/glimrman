#!/usr/bin/env python
import os
import logging
from pprint import pprint

import spotipy
from spotipy import util
import sqlalchemy
from sqlalchemy.orm import sessionmaker

from .models import *

log = logging.getLogger(__name__)


def get_playlist_tracks(sp, username, playlist_id):
    '''
    Parameters
    ----------
    sp : Spotipy
    username : str
    playlist_id : str
    '''
    playlist = sp.user_playlist(username, playlist_id, 
                                fields='tracks,next')

    def get_tracks(tracks):
        for item in tracks['items']:
            track = item['track']

            # log.info('%32.32s - %s (duration: %dm | id: %s)' % (track['artists'][0]['name'], 
            #                                                     track['name'],
            #                                                     track['duration_ms'] / 1000.0 / 60,
            #                                                     track['id']))
            yield track

    # Iterate over pages
    tracks = playlist['tracks']
    for track in get_tracks(tracks):
        yield track
    
    while tracks['next']:
        tracks = sp.next(tracks)
        for track in get_tracks(tracks):
            yield track


def get_all_playlist_tracks(sp, username, skip_playlists=None):
    '''
    Parameters
    ----------
    sp : Spotipy
    username : str
    skip_playlists : [playlist_id]
    '''
    if skip_playlists is None:
        skip_playlists = []

    for playlist in sp.user_playlists(username)['items']:
        playlist_id = playlist['id']
        if playlist_id in skip_playlists:
            continue

        # log.info('%s (tracks: %d | id: %s)' % (playlist['name'], 
        #                                        playlist['tracks']['total'], 
        #                                        playlist['id']))

        for track in get_playlist_tracks(sp, username, playlist_id):
            yield track


def init_database_session(config):
    '''
    '''
    log.debug('Initializing database %s...' % config['DATABASE_URI'])
    engine = sqlalchemy.create_engine(config['DATABASE_URI'], 
                                      echo=config['SQLALCHEMY_ECHO'])
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    return session


def init_spotify_client(config):
    '''
    '''
    log.debug('Initializing Spotify client...')
    os.environ['SPOTIPY_CLIENT_ID'] = config['CLIENT_ID']
    os.environ['SPOTIPY_CLIENT_SECRET'] = config['CLIENT_SECRET']
    os.environ['SPOTIPY_REDIRECT_URI'] = config['REDIRECT_URI']
    auth_scopes = [
        'playlist-read-private',
        'playlist-read-collaborative',
        'playlist-modify-public',
        'playlist-modify-private'
    ]
    token = util.prompt_for_user_token(config['AUTH_USERNAME'], ' '.join(auth_scopes))
    sp = spotipy.Spotify(token)
    return sp


def sync():
    # TODO: Use ConfigParser instead
    config = {
        'CLIENT_ID': '21c5b124594141f18127e788449ff5d9',
        'CLIENT_SECRET': '482686566a0f41dba79bc33629f45f1a',
        'REDIRECT_URI': 'http://www.lumapictures.com',
        #'DATABASE_URI': 'mysql://root@127.0.0.1/spotify?charset=utf8&use_unicode=0'
        'DATABASE_URI': 'sqlite:///tracks.db',
        'SQLALCHEMY_ECHO': False,
        'AUTH_USERNAME': '126673939',  # chris lyon
        'PLAYLIST_USERNAME': 'lumapictures',
        'SKIP_PLAYLISTS': [
            '6S8fBNT2hnO67upDYOm0yB'  # FIKA
        ],
        'FINAL_PLAYLIST': '6BZ3HtHbCUyJqJn5bKSqAw'
    }

    session = init_database_session(config)
    sp = init_spotify_client(config)

    # Add tracks in all playlists to database
    playlist_username = config['PLAYLIST_USERNAME']
    log.info('Getting tracks in all playlists for %s...' % playlist_username)
    for track in get_all_playlist_tracks(sp, playlist_username, config['SKIP_PLAYLISTS']):
        track_id = track['id']
        track_obj = session.query(Track).filter(Track.id == track_id).first()
        if track_obj is None:
            # Add track to database
            session.add(Track(id=track['id'],
                              artist=track['artists'][0]['name'],
                              name=track['name'],
                              duration_ms=track['duration_ms']))

    session.commit()

    final_playlist = config['FINAL_PLAYLIST']
    auth_username = config['AUTH_USERNAME']
    existing_ids = set([track['id'] for track in get_playlist_tracks(sp, auth_username, final_playlist)])

    # Remove all current tracks
    if len(existing_ids) > 0:
        log.info('Removing tracks: %s' % ', '.join(existing_ids))
        sp.user_playlist_remove_all_occurrences_of_tracks(auth_username, final_playlist, existing_ids)

    # Add new tracks
    query = session.query(Track)
    track_ids = set([tr.id for tr in query.all() if tr.rating > -1])
    ids_to_add = track_ids #- existing_ids
    if len(ids_to_add) > 0:
        log.info('Adding tracks: %s' % ', '.join(ids_to_add))
        sp.user_playlist_add_tracks(auth_username, final_playlist, track_ids)


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s | %(levelname)-5s | %(name)s: %(message)s')
    logging.getLogger('requests').setLevel(logging.WARN)
    sync()


if __name__ == '__main__':
    main()
