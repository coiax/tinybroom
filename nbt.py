from __future__ import print_function

import collections
import gzip

import bitstring

TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10
TAG_INT_ARRAY = 11

ALL_TAGS = (0,1,2,3,4,5,6,7,8,9,10,11)
SIMPLE_TAGS = (TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG, TAG_FLOAT, TAG_DOUBLE)

def open_file(fileish, compressed=True):
    try:
        fileish.read
    except AttributeError:
        is_file = False
    else:
        is_file = True

    if is_file:
        if compressed:
            fileish = gzip.GzipFile(fileobj=fileish)
        stream = bitstring.ConstBitStream(auto=fileish)
    else:
        if compressed:
            fileish = gzip.GzipFile(filename=fileish)
            stream = bitstring.ConstBitStream(auto=fileish)
        else:
            stream = bitstring.ConstBitStream(filename=fileish)

    return stream

def read_file(filename, compressed=True):
    if compressed:
        gzfile = gzip.GzipFile(filename=filename)
        contents = gzfile.read()
        gzfile.close()
    else:
        with open(filename, 'rb') as f:
            contents = f.read()
    stream = bitstring.ConstBitStream(bytes=contents)
    nbt = read_nbt(stream)
    return nbt

def read_string(bytes):
    return read_nbt(bitstring.ConstBitStream(bytes=bytes))

def read_nbt(stream):
    return get_named_tag(stream)

    assert False # really shouldn't end up here

TAG_END_MARKER = object()
def get_named_tag(stream):
    tag_type = get_payload(stream, TAG_BYTE)

    assert tag_type in ALL_TAGS

    if tag_type == TAG_END:
        return TAG_END_MARKER

    name = get_payload(stream, TAG_STRING)

    payload = get_payload(stream, tag_type)

    return name, payload

def get_payload(stream, tag_type):
    payload = None

    if tag_type == TAG_END:
        payload = TAG_END_MARKER
    elif tag_type == TAG_BYTE:
        payload = stream.read('int:8')
    elif tag_type == TAG_SHORT:
        payload = stream.read('intbe:16')
    elif tag_type == TAG_INT:
        payload = stream.read('intbe:32')
    elif tag_type == TAG_LONG:
        payload = stream.read('intbe:64')
    elif tag_type == TAG_FLOAT:
        payload = stream.read('floatbe:32')
    elif tag_type == TAG_DOUBLE:
        payload = stream.read('floatbe:64')
    elif tag_type == TAG_BYTE_ARRAY:
        size = get_payload(stream, TAG_INT)
        some_bytes = []
        for i in range(size):
            some_bytes.append(get_payload(stream, TAG_BYTE))
        payload = some_bytes
    elif tag_type == TAG_STRING:
        length = get_payload(stream, TAG_SHORT)
        some_string_bytes = stream.read('bytes:{}'.format(length))
        some_string = some_string_bytes.decode('utf-8')
        payload = some_string
    elif tag_type == TAG_LIST:
        inner_tag_type = get_payload(stream, TAG_BYTE)
        size = get_payload(stream, TAG_INT)
        some_payloads = []
        for i in range(size):
            some_payloads.append(get_payload(stream, inner_tag_type))
        payload = some_payloads
    elif tag_type == TAG_INT_ARRAY:
        size = get_payload(stream, TAG_INT)
        some_ints = []
        for i in range(size):
            some_ints.append(get_payload(stream, TAG_INT))
        payload = some_ints
    elif tag_type == TAG_COMPOUND:
        fully_formed_tags = collections.OrderedDict()
        while True:
            # item is either a (name, payload) or a None
            item = get_named_tag(stream)
            if item is TAG_END_MARKER:
                break
            else:
                name, payload = item
                fully_formed_tags[name] = payload
        payload = fully_formed_tags

    assert payload is not None

    return payload

if __name__=='__main__':
    nbt = read_file('level.dat', compressed=True)
