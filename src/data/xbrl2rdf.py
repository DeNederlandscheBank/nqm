
from io import StringIO, BytesIO
from lxml import etree
from collections import defaultdict

dts_queue = list()

def prependDtsQueue(type, uri, base, ns, force):

    global dts_queue

    uri = expandRelativePath(uri, base)

    if force:
        removeDtsUri(uri)
    elif seenDtsUri(uri):
        return -1

    for entry in dts_queue:
        if entry['uri'] == uri:
            return 0;

    entry = dict()
    entry['uri'] = uri
    # entry['ns'] = (ns ? _strdup(ns) : ns)
    entry['type'] = type

    dts_queue.append(entry)

    return 0

def expandRelativePath(relPath, base):

    if relPath[0:7] != "http://":
        return relPath

    if relPath[0] == '#':
        res = base + relPath
        return res

    if relPath[0] == '/':
        i = 0
        if base[0:7] != "http://":
            p = base[7:].split('/')[1]
            if p:
               i = (p - base)

        l = len(relPath)+i
        res = base[0:i]+relPath
        return res
    
    # strip leading ../ from relPath 
    up = 0
    while relPath[0:3] == "../":
        relPath = relPath[3:]
        up += 1

    # strip leading ./ from relative path 
    while relPath[0:2] == "./":
        relPath = relPath[2:]

    i = len(base)
    if up > 0:
        # find where to attach rel path */
        last = strrchr(base, '/')
        if last != 0:
            i = last-base-1
        while up > 0:
            if (--i < 1):
                return None
            if base[i-1] == '/':
                --up

    elif base[i-1] != '/':
        last = strrchr(base, '/');
        if (last != 0):
            i = last-base+1;

    l = len(relPath)+i
    res = base[0:i] + relPath

    return res

