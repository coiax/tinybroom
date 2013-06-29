#!/usr/bin/pypy

import collections
import gzip
import zlib
import StringIO
import hashlib

import bitstring

import nbt

try:
    import memcache
except ImportError:
    pass

class _MemcacheCache(object):
    def __init__(self, prefix=''):
        self.mc = memcache.Client(['127.0.0.1:11211'], debug=1)
        self.prefix = prefix
    def _keyify(self, key):
        key = ''.join((self.prefix, repr(key)))
        memcache_key = hashlib.md5(key).hexdigest()
        return memcache_key
    def __getitem__(self, key):
        item = self.mc.get(self._keyify(key))
        return item
    def __setitem__(self, key, value):
        self.mc.set(self._keyify(key), value)

class _NoopCache(object):
    def __getitem__(self, key):
        return None
    def __setitem__(self, key, value):
        return None

CHUNK_OFFSET = {}
for z in range(32):
    for x in range(32):
        CHUNK_OFFSET[x,z] = 4 * ((x % 32) + (z % 32)*32)

def read_region_from_file(filename, cache=None):
    stream = bitstring.ConstBitStream(filename=filename)
    region = read_region(stream, cache=cache)
    return region

def read_region(stream, keep_empty=True, cache=None):
    chunks = collections.OrderedDict()
    if cache is None:
        cache = _NoopCache()

    for z in range(32):
        for x in range(32):
            offset, length = get_location(stream)
            chunks[x,z] = {'offset': offset, 'length': length}
            chunks[x,z]['empty'] = offset == 0 and length == 0

    skip_chunk = []

    for z in range(32):
        for x in range(32):
            chunks[x,z]['timestamp'] = get_timestamp(stream)
            cached_chunk = cache[x,z]
            if cached_chunk is not None:
                if cached_chunk['timestamp'] <= chunks[x,z]['timestamp']:
                    #print("Skipping chunk ({},{}); in cache".format(x,z))
                    skip_chunk.append((x,z))
                else:
                    chunks[x,z] = cached_chunk

    for x,z in chunks.keys():
        if not chunks[x,z]['empty'] and (x,z) not in skip_chunk:
            #print("Reading chunk ({},{})".format(x,z))
            stream.pos = chunks[x,z]['offset'] * 4096 * 8
            data = read_chunk(stream)
            chunks[x,z]['data'] = nbt.read_string(data)

            cache[x,z] = chunks[x,z]

    doomed = []

    if not keep_empty:
        for key in chunks.keys():
            if chunks[key]['empty']:
                doomed.append(key)

    for key in doomed:
        del chunks[key]

    return chunks

def read_chunk(stream):
    start_pos = stream.pos

    length = stream.read('intbe:32')
    compression_type = stream.read('int:8')
    compressed_data = stream.read('bytes:{}'.format(length - 1))

    # Then some padding. Work out how much.
    current_pos = stream.pos
    remaining = (4096 * 8) - current_pos % (4096 * 8)

    stream.pos = stream.pos + remaining

    assert compression_type in (1,2)
    # Now decompress the data.
    if compression_type == 1:
        # Gzip. Apparently unused.
        io = StringIO.StringIO(compressed_data)
        with gzip.GzipFile(fileobj=io) as f:
            uncompressed = f.read()
        io.close()
    elif compression_type == 2:
        uncompressed = zlib.decompress(compressed_data)

    return uncompressed


def get_location(stream):
    offset = stream.read('intbe:24')
    length = stream.read('int:8')
    return offset, length

def get_timestamp(stream):
    return stream.read('intbe:32')

if __name__=='__main__':
    import pickle
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('region_file',nargs='?',default='r.-1.0.mca')
    p.add_argument('--memcache',action='store_true')

    ns = p.parse_args()

    if ns.memcache:
        import memcache
        cache = _MemcacheCache(prefix=ns.region_file)
    else:
        cache = None

    region = read_region_from_file(ns.region_file, cache=cache)
