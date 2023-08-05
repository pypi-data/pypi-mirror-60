#-*- coding:utf-8 -*-
import requests
import time
from ..torrent import Torrent
from ..torrentstatus import TorrentStatus
from ..exception.loginfailure import LoginFailure
from ..exception.deletionfailure import DeletionFailure
from ..exception.connectionfailure import ConnectionFailure
from ..exception.incompatibleapi import IncompatibleAPIVersion

class qBittorrent(object):
    # API Handler for v1
    class qBittorrentAPIHandlerV1(object):
        def __init__(self, host):
            # Host
            self._host = host
            # Requests Session
            self._session = requests.Session()
        
        # Check API Compatibility
        def check_compatibility(self):
            request = self._session.get(self._host+'/version/api')
            return request.status_code != 404 # compatible if API exsits

        # Get API major version
        def api_major_version(self):
            return 'v1'
        
        # Get API version
        def api_version(self):
            return self._session.get(self._host+'/version/api')

        # Get client version
        def client_version(self):
            return self._session.get(self._host+'/version/qbittorrent')
        
        # Login
        def login(self, username, password):
            return self._session.post(self._host+'/login', data={'username':username, 'password':password})

        # Get torrent list
        def torrent_list(self):
            return self._session.get(self._host+'/query/torrents')
        
        # Get torrent's generic properties
        def torrent_generic_properties(self, torrent_hash):
            return self._session.get(self._host+'/query/propertiesGeneral/'+torrent_hash)
        
        # Get torrent's tracker
        def torrent_trackers(self, torrent_hash):
            return self._session.get(self._host+'/query/propertiesTrackers/'+torrent_hash)
        
        # Delete torrent
        def delete_torrent(self, torrent_hash):
            return self._session.post(self._host+'/command/delete', data={'hashes':torrent_hash})
        
        # Delete torrent and data
        def delete_torrent_and_data(self, torrent_hash):
            return self._session.post(self._host+'/command/deletePerm', data={'hashes':torrent_hash})

    # API Handler for v2
    class qBittorrentAPIHandlerV2(object):
        def __init__(self, host):
            # Host
            self._host = host
            # Requests Session
            self._session = requests.Session()
        
        # Check API Compatibility
        def check_compatibility(self):
            request = self._session.get(self._host+'/api/v2/app/webapiVersion')
            return request.status_code != 404 # compatible if API exsits

        # Get API major version
        def api_major_version(self):
            return 'v2'
        
        # Get API version
        def api_version(self):
            return self._session.get(self._host+'/api/v2/app/webapiVersion')

        # Get client version
        def client_version(self):
            return self._session.get(self._host+'/api/v2/app/version')
        
        # Login
        def login(self, username, password):
            return self._session.post(self._host+'/api/v2/auth/login', data={'username':username, 'password':password})

        # Get torrent list
        def torrent_list(self):
            return self._session.get(self._host+'/api/v2/torrents/info')
        
        # Get torrent's generic properties
        def torrent_generic_properties(self, torrent_hash):
            return self._session.get(self._host+'/api/v2/torrents/properties', params={'hash': torrent_hash})
        
        # Get torrent's tracker
        def torrent_trackers(self, torrent_hash):
            return self._session.get(self._host+'/api/v2/torrents/trackers', params={'hash':torrent_hash})
        
        # Delete torrent
        def delete_torrent(self, torrent_hash):
            return self._session.get(self._host+'/api/v2/torrents/delete', params={'hashes':torrent_hash, 'deleteFiles': False})
        
        # Delete torrent and data
        def delete_torrent_and_data(self, torrent_hash):
            return self._session.get(self._host+'/api/v2/torrents/delete', params={'hashes':torrent_hash, 'deleteFiles': True})

    def __init__(self, host):
        # Torrents list cache
        self._torrents_list_cache = []
        self._refresh_cycle = 30
        self._refresh_time = 0

        # Request Handler
        self._request_handler = None
        for obj in [self.qBittorrentAPIHandlerV2, self.qBittorrentAPIHandlerV1]: # New version API first
            handler = obj(host)
            if handler.check_compatibility():
                self._request_handler = handler
                break
        if self._request_handler is None:
            raise IncompatibleAPIVersion('Incompatible qbittorrent client. The current API version may be unsupported.')

    # Login to qBittorrent
    def login(self, username, password):
        try:
            request = self._request_handler.login(username, password)
        except Exception as exc:
            raise ConnectionFailure(str(exc))
        
        if request.status_code == 200:
            if request.text == 'Fails.': # Fail
                raise LoginFailure(request.text)
        else:
            raise LoginFailure('The server returned HTTP %d.' % request.status_code)
    
    # Get qBittorrent Version
    def version(self):
        request = self._request_handler.client_version()
        return ('qBittorrent %s' % request.text)
    
    # Get API version
    def api_version(self):
        return ('%s (%s)' % (self._request_handler.api_version().text, self._request_handler.api_major_version()))
    
    # Get Torrents List
    def torrents_list(self):
        # Request torrents list
        torrent_hash = []
        request = self._request_handler.torrent_list()
        result = request.json()
        # Save to cache
        self._torrents_list_cache = result
        self._refresh_time = time.time()
        # Get hash for each torrent
        for torrent in result:
            torrent_hash.append(torrent['hash'])
        return torrent_hash
    
    # Get Torrent Properties
    def torrent_properties(self, torrent_hash):
        if time.time() - self._refresh_time > self._refresh_cycle: # Out of date
            self.torrents_list()
        for torrent in self._torrents_list_cache:
            if torrent['hash'] == torrent_hash:
                # Get other information
                properties = self._request_handler.torrent_generic_properties(torrent_hash).json()
                trackers = self._request_handler.torrent_trackers(torrent_hash).json()
                return Torrent(
                    torrent['hash'], torrent['name'],
                    torrent['category'] if 'category' in torrent else torrent['label'],
                    [tracker['url'] for tracker in trackers],
                    qBittorrent._judge_status(torrent['state']), 
                    torrent['state'] == 'stalledUP' or torrent['state'] == 'stalledDL',
                    torrent['size'], torrent['ratio'],
                    properties['total_uploaded'], properties['addition_date'],
                    properties['seeding_time'])

    # Judge Torrent Status (qBittorrent doesn't have stopped status)
    @staticmethod
    def _judge_status(state):
        if state == 'downloading' or state == 'stalledDL':
            status = TorrentStatus.Downloading
        elif state == 'queuedDL' or state == 'queuedUP':
            status = TorrentStatus.Queued
        elif state == 'uploading' or state == 'stalledUP':
            status = TorrentStatus.Uploading
        elif state == 'checkingUP' or state == 'checkingDL':
            status = TorrentStatus.Checking
        elif state == 'pausedUP' or state == 'pausedDL':
            status = TorrentStatus.Paused
        else:
            status = TorrentStatus.Unknown
        return status
    
    # Remove Torrent
    def remove_torrent(self, torrent_hash):
        request = self._request_handler.delete_torrent(torrent_hash)
        if request.status_code != 200:
            raise DeletionFailure('Cannot delete torrent %s. The server responses HTTP %d.' % (torrent_hash, request.status_code))
    
    # Remove Torrent and Data
    def remove_data(self, torrent_hash):
        request = self._request_handler.delete_torrent_and_data(torrent_hash)
        if request.status_code != 200:
            raise DeletionFailure('Cannot delete torrent %s and its data. The server responses HTTP %d.' % (torrent_hash, request.status_code))