#!/usr/bin/env python3
# coding: utf-8

import logging
import time

import requests
from joker.diskcache.base import DiskCache


logger = logging.getLogger(__name__)


class CachedResponse(object):
    __slots__ = ['content', 'httpmeta']

    status_code = 200
    reason = 'Cached'
    fields = ['status_code', 'reason', 'encoding', 'url']

    def __init__(self, content, httpmeta):
        self.content = content
        self.httpmeta = httpmeta

    def __getattr__(self, name):
        return self.httpmeta.get(name)

    @classmethod
    def convert(cls, response):
        httpmeta = {k: getattr(response, k, None) for k in cls.fields}
        return cls(response.content, httpmeta)

    @property
    def text(self):
        import chardet
        encoding = chardet.detect(self.content)['encoding']
        return self.content.decode(encoding)


class HTTPCache(DiskCache):
    def save(self, key, response, compression=None):
        if key is None:
            return
        meta = {'httpmeta': CachedResponse.convert(response).httpmeta}
        self._save(key, meta, response.content, compression)

    def load(self, key, check=False):
        if key is None:
            return
        meta_and_content = self._load(key, check)
        if meta_and_content:
            meta, content = meta_and_content
            httpmeta = meta.get('httpmeta', {})
            return CachedResponse(content, httpmeta)


class DummyCache(object):
    def load(self, key):
        pass

    def save(self, key, content):
        pass


class HTTPClient(object):
    def __init__(self, cache):
        self.cache = cache
        self.sess = requests.Session()

    @classmethod
    def cached(cls, dirpath, algo='sha1', prefixlen=4):
        return cls(HTTPCache(dirpath, algo=algo, prefixlen=prefixlen))

    @classmethod
    def cacheless(cls):
        return cls(DummyCache())

    @staticmethod
    def keygen(url, **kwargs):
        method = kwargs.get('method', 'get')
        if method.lower() == 'get':
            return url

    @staticmethod
    def pause(maxsec):
        if maxsec <= 0:
            return
        time.sleep(time.time() % maxsec)

    def request(self, url, **kwargs):
        if not url:
            self.sess.headers.pop('Referer', 0)
            return
        key = self.keygen(url, **kwargs)
        resp = self.cache.load(key)
        if resp is None:
            logger.debug('cache miss: %s', url)
            kwargs.setdefault('method', 'get')
            resp = self.sess.request(url=url, **kwargs)
            self.cache.save(key, resp)
        self.sess.headers['Referer'] = url
        return resp

    def post(self, url, **kwargs):
        kwargs.setdefault('method', 'post')
        return self.request(url, **kwargs)

    def get(self, url):
        return self.request(url)

    def batch_get(self, targets):
        for tar in targets:
            if isinstance(tar, (int, float)):
                yield self.pause(tar)
            yield self.get(tar)
