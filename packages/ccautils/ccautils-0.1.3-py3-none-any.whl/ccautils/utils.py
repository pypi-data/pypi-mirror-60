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
""" utils.py

a set of utilities for python programmes and scripts
"""
import os
import sys
from ccautils.errors import errorRaise


def addToString(xstr, xadd):
    """ appends the string `xadd` to the string `xstr`

    if xadd is a list then each list member that is a string
    is appended to xstr
    """
    try:
        if type(xstr) is str:
            op = xstr
        else:
            op = ""
        if type(xadd) is list:
            for xi in xadd:
                if type(xi) is str:
                    op += xi
        else:
            op += xadd
        return op
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def delimitString(xstr, delimeter=" - "):
    try:
        op = ""
        xlist = None
        if type(xstr) is str:
            xlist = xstr.split(" ")
        elif type(xstr) is list:
            xlist = xstr
        if xlist is None:
            raise ValueError("delimitString: parameter must be string or list")
        for xl in xlist:
            if len(op) > 0:
                op += delimeter + xl
            else:
                op = xl
        return op
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


# def delimitString(xstr, xadd, delimeter=" - "):
#     try:
#         if type(xadd) is list:
#             nlst = []
#             for i in xadd:
#                 nlst.append(delimeter)
#                 nlst.append(i)
#             return addToString(xstr, nlst)
#         else:
#             return addToString(xstr, [delimeter, addstr])
#     except Exception as e:
#         fname = sys._getframe().f_code.co_name
#         errorRaise(fname, e)


def makeDictFromString(istr):
    """ makes a dictionary from a string of parameters

    leading and trailing white space is stripped

    params:
        istr: a string in the form:
            'someparam= somevalue,someotherparam =someothervalue  '

    returns a dictionary:
        {"someparam": "somevalue", "someotherparam": "someothervalue"}
    """
    try:
        pd = {}
        if "=" in istr:
            ea = istr.split(",")
            for p in ea:
                tmp = p.split("=")
                pd[tmp[0].strip()] = tmp[1].strip()
        return pd
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def askMe(q, default):
    try:
        ret = default
        val = input(f"{q} ({default}) > ")
        if len(val) > 0:
            ret = val
        return ret
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def padStr(xstr, xlen=2, pad=" ", padleft=True):
    try:
        zstr = xstr
        while len(zstr) < xlen:
            if padleft:
                zstr = pad + zstr
            else:
                zstr += pad
        return zstr
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def reduceTime(unit, secs):
    try:
        rem = units = 0
        if unit > 0:
            units = int(secs / unit)
            rem = int(secs % unit)
        else:
            raise ValueError(
                f"divide by zero requested in reduceTime: unit: {unit}, secs: {secs}"
            )
        return (units, rem)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def displayValue(val, label, zero=True):
    try:
        if zero and val == 0:
            return ""
        dlabel = label if val == 1 else label + "s"
        return addToString(str(val), [" ", dlabel])
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def secondsFromHMS(shms):
    """
    convert "01:02:32.47" to seconds
    """
    try:
        hrs = mins = secs = extra = 0
        xtmp = shms.split(".")
        if int(xtmp[1]) > 50:
            extra = 1
        tmp = xtmp[0].split(":")
        cn = len(tmp)
        if cn == 3:
            hrs = int(tmp[0])
            mins = int(tmp[1])
            secs = int(tmp[2])
        elif cn == 2:
            mins = int(tmp[0])
            secs = int(tmp[1])
        elif cn == 1:
            secs = int(tmp[0])
        return (hrs * 3600) + (mins * 60) + secs + extra
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def hms(secs, small=True, short=True, single=False):
    """ convert `secs` to days, hours, minutes and seconds

    if `small` is True then only return the higher values
    if they are > zero

    if `short` is True then the labels are their short form

    if `single` is True then the labels are single letters
    """
    try:
        labels = ["day", "hour", "minute", "second"]
        shorts = ["day", "hour", "min", "sec"]
        singles = ["d", "h", "m", "s"]
        tim = [0, 0, 0, 0]
        op = []
        onemin = 60
        onehour = onemin * 60
        oneday = onehour * 24
        tim[0], rem = reduceTime(oneday, secs)
        tim[1], rem = reduceTime(onehour, rem)
        tim[2], tim[3] = reduceTime(onemin, rem)
        started = not small
        if single:
            xlabs = singles
        else:
            xlabs = shorts if short else labels
        for cn in range(4):
            if not started:
                if tim[cn] > 0:
                    started = True
            if started:
                delim = " " if single else ", "
                if cn == 3:
                    delim = " " if single else " and "
                if len(op) > 0:
                    op.append(delim)
                if single:
                    sval = str(tim[cn]) + xlabs[cn]
                else:
                    sval = displayValue(tim[cn], xlabs[cn], zero=False)
                op.append(sval)
        msg = addToString("", op)
        return msg
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
