#!/usr/bin/pypy

import collections
import gzip
import zlib
import StringIO

import bitstring

import nbt

CHUNK_OFFSET = {}
for z in range(32):
    for x in range(32):
        CHUNK_OFFSET[x,z] = 4 * ((x % 32) + (z % 32)*32)

def read_region_from_file(filename):
    stream = bitstring.ConstBitStream(filename=filename)
    region = read_region(stream)
    return region

def read_region(stream, keep_empty=True):
    chunks = collections.OrderedDict()

    for z in range(32):
        for x in range(32):
            offset, length = get_location(stream)
            chunks[x,z] = {'offset': offset, 'length': length}
            chunks[x,z]['empty'] = offset == 0 and length == 0

    for z in range(32):
        for x in range(32):
            chunks[x,z]['timestamp'] = get_timestamp(stream)

    for x,z in chunks.keys():
        if not chunks[x,z]['empty']:
            print("Reading chunk ({},{})".format(x,z))
            stream.pos = chunks[x,z]['offset'] * 4096 * 8
            data = read_chunk(stream)
            chunks[x,z]['data'] = nbt.read_string(data)

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
    ns = p.parse_args()

    region = read_region_from_file(ns.region_file)
    with open('_region_cache.pickle','wb') as f:
        pickle.dump(region, f, -1)
