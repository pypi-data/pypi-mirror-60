# Copyright (c) 2018, Christopher Allison
#
#     This file is part of ccautils.
#
#     ccautils is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     ccautils is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with ccautils.  If not, see <http://www.gnu.org/licenses/>.
""" fileutils.py

a set of file based utilities for python programmes and scripts
"""
import os
import sys
import hashlib
from pathlib import Path
import ccautils.utils as UT
from ccautils.errors import errorRaise


def fileExists(fqfn):
    try:
        return Path(fqfn).is_file()
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def dirExists(fqdn):
    try:
        return Path(fqdn).is_dir()
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def dfExists(fqdfn):
    try:
        ret = fileExists(fqdfn)
        if not ret:
            ret = dirExists(fqdfn)
        return ret
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def makePath(pn):
    try:
        if not dirExists(pn):
            p = Path(pn)
            p.mkdir(mode=0o755, parents=True, exist_ok=True)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def makeFilePath(fqfn):
    try:
        pfn = os.path.basename(fqfn)
        makePath(pfn)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def absPath(fn):
    try:
        return os.path.abspath(os.path.expanduser(fn))
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def rename(src, dest):
    try:
        if dfExists(src):
            p = Path(src)
            p.rename(dest)
        else:
            raise Exception(f"src file does not exist: {src}")
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def fileDelete(fqfn):
    try:
        if fileExists(fqfn):
            os.unlink(fqfn)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def fileSize(fqfn):
    try:
        if fileExists(fqfn):
            return os.stat(fqfn).st_size
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def sizeof_fmt(num, suffix="B"):
    """
    from article by Fred Cirera:
    https://web.archive.org/web/20111010015624/http://blogmag.net/blog/read/38/Print_human_readable_file_size
    and stackoverflow:
    https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return "{num:3.1f}Y{suffix}"


def getFileHash(fqfn, blocksize=65536):
    """
    returns a tuple of the sha256 hash and filesize
    of the named file.
    """
    try:
        fnsize = fileSize(fqfn)
        sha = hashlib.sha256()
        with open(fqfn, "rb") as ifn:
            fbuf = ifn.read(blocksize)
            while len(fbuf) > 0:
                sha.update(fbuf)
                fbuf = ifn.read(blocksize)
        return (sha.hexdigest(), fnsize)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def fileTouch(fqfn, truncate=True):
    """ 'touches' the `fqfn` file

    it is truncated if `truncate` is True and
    the file exists already, otherwise the
    access timestamp is just updated
    """
    try:
        if fileExists(fqfn) and truncate:
            junk = open(fqfn, "w").close()
        elif fileExists(fqfn):
            junk = open(fqfn, "r").close()
        else:
            junk = open(fqfn, "w").close()
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def readFile(fqfn):
    try:
        op = None
        if os.path.exists(fqfn):
            with open(fqfn, "r") as ifn:
                lines = ifn.readlines()
            op = UT.addToString(op, lines)
        return op
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
