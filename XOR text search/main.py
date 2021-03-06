#
# XOR text search - Search XORed / bit-rotated string in selected region (the
# whole file if not selected)
#
# Copyright (c) 2012, 2013, Nobutaka Mantani
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

LEN_AFTER_HIT = 50

# Masking bits
def mask(x):
   if (x >= 0):
       return 2 ** x - 1
   else:
       return 0

# Bitwise rotate right
def ror(x, rot=1):
    rot %= 8
    if (rot < 1):
        return x
    x &= mask(8)
    return (x >> rot) | ((x << (8 - rot)) & mask(8))

# Bitwise rotate left
def rol(x, rot=1):
    rot %= 8
    if (rot < 1):
        return x
    x &= mask(8)
    return ((x << rot) & mask(8)) | (x >> (8 - rot))

# Make dictionary of values in data
def valdict(buf):
    values = {}
    b = list(buf)
    length = len(b)

    for i in range(0, length):
        v = ord(b[i])
        if (v not in values):
            values[v] = True

    return values

# Search XORed string
def search_xor(buf, offset, length, keyword):
    values = valdict(buf)
    num_hits = 0

    for i in range(0, length):
        v = ord(buf[i])
        if (v not in values):
            values[v] = True

    for i in range(0, 256):
        pattern = keyword[:]
        notinvalues = False
        hits = []

        # Encode search string and check whether the values of encoded string exist in data
        for j in range(0, len(pattern)):
            pattern[j] = chr(ord(pattern[j]) ^ i)
            if (ord(pattern[j]) not in values):
                notinvalues = True
                break

        # Skip search if the values of encoded string don't exist in data
        if (notinvalues):
            continue

        pos = buf.find("".join(pattern), 0)

        if (pos != -1):
            hits.append(pos)

        while (pos != -1):
            pos = buf.find("".join(pattern), pos + len(pattern))
            if (pos != -1):
                hits.append(pos)

        # Print search hits
        for j in hits:
            end = j + len(pattern) + LEN_AFTER_HIT
            if (end < length):
                hitstr = list(buf[j:end])
            else:
                hitstr = list(buf[j:])

            for k in range(0, len(hitstr)):
                c = ord(hitstr[k]) ^ i
                if (c < 0x20 or c > 0x126):
                    c = 0x2e
                hitstr[k] = chr(c)

            print "XOR key: 0x%02x offset: 0x%x search hit: %s" % (i, offset + j, "".join(hitstr))
            setBookmark(offset + j, len(keyword), hex(offset + j), "#c8ffff")
            num_hits += 1

    return num_hits

# Search bit-rotated string
def search_rol(buf, offset, length, keyword):
    values = valdict(buf)
    num_hits = 0

    for i in range(1, 8):
        pattern = keyword[:]
        notinvalues = False
        hits = []

        # Encode search string and check whether the values of encoded string exist in data
        for j in range(0, len(pattern)):
            pattern[j] = chr(ror(ord(pattern[j]), i))
            if (ord(pattern[j]) not in values):
                notinvalues = True
                break

        # Skip search if the values of encoded string don't exist in data
        if (notinvalues):
            continue

        pos = buf.find("".join(pattern), 0)

        if (pos != -1):
            hits.append(pos)

        while (pos != -1):
            pos = buf.find("".join(pattern), pos + len(pattern))
            if (pos != -1):
                hits.append(pos)

        # Print search hits
        for j in hits:
            end = j + len(pattern) + LEN_AFTER_HIT
            if (end < length):
                hitstr = list(buf[j:end])
            else:
                hitstr = list(buf[j:])

            for k in range(0, len(hitstr)):
                c = rol(ord(hitstr[k]), i)
                if (c < 0x20 or c > 0x126):
                    c = 0x2e
                hitstr[k] = chr(c)

            print "ROL bit: %d offset: 0x%x search hit: %s" % (i, offset + j, "".join(hitstr))
            setBookmark(offset + j, len(keyword), hex(offset + j), "#c8ffff")
            num_hits += 1

    return num_hits

length_sel = getSelectionLength()
offset = getSelectionOffset()
keyword = list(showSimpleDialog("Search keyword:"))

if (len(keyword) > 0):
    if (length_sel > 0):
        length = length_sel
        buf = getSelection()
        print "Search XORed / bit-rotated string from offset %s to %s with keyword '%s'" % (hex(offset), hex(offset + length - 1), "".join(keyword))
    else:
        buf = getDocument()
        length = getLength()
        offset = 0
        print "Search XORed / bit-rotated string in the whole file with keyword '%s'" % "".join(keyword)
    num_xor = search_xor(buf, offset, length, keyword)
    num_rol = search_rol(buf, offset, length, keyword)
    if num_xor + num_rol == 1:
        print "Added a bookmark to the search hit."
    elif num_xor + num_rol > 1:
        print "Added bookmarks to the search hits."

