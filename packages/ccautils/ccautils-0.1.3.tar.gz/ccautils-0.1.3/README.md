# ccautils

a set of utilities for python3.6+ programmes and scripts.

<a name=headdd></a>
* [Install](#install)
* [Development](#devel)
* [Testing](#testing)
* [Miscellaneous Utilities](#utils)
    * [Usage](#uusage)
* [File Utilities](#futils)
    * [Usage](#fusage)


<a name=install></a>
## [Install](#headdd)

Install for the user:
```
pip3 install ccautils --user
```

Install for a virtual environment:
```
pip install ccautils
```

<a name=devel></a>
## [Development](#headdd)

I use [poetry](https://python-poetry.org/) to manage these utilities.
Clone this repository and install `poetry`, then install the dependancies.

```
git clone https://github.com/ccdale/ccautils.git
cd ccautils
poetry install
```

<a name=testing></a>
## [Testing](#headdd)
To run the tests you must have `pytest` and `poetry` installed.

```
poetry install
poetry run pytest
```

<a name=utils></a>
## [Miscellaneous Utilities](#headdd)

<a name=uusage></a>
### [Usage](#headdd)

```
import ccautils.utils as UT
```

<a name=menu></a>
* [addToString](#addtostring)
* [delimitString](#delimitstring)
* [makeDictFromString](#makedictfromstring)
* [askMe](#askme)
* [padStr](#padstr)
* [reduceTime](#reducetime)
* [displayValue](#displayvalue)
* [secondsFromHMS](#secondsfromhms)
* [hms](#hms)

<a name=addtostring></a>
### [addToString(xstr, xadd)](#menu)

[Code](https://github.com/ccdale/ccautils/blob/master/ccautils/utils.py#L26)

Returns a string with `xadd` appended to `xstr`.  If `xadd` is a list, all
`str` members of the list will be appended in order.

```
UT.addToString("hello", [" ", "world"])

> "hello world"
```

<a name=delimitstring></a>
### [delimitString(xstr, delimeter=" - ")](#menu)

[Code](https://github.com/ccdale/ccautils/blob/master/ccautils/utils.py#L49)

`xstr` can be a list or a string.  If it is a string, it is spit apart at
spaces and delimeted with `delimeter`.  If it is a list, each member is
delimeted with `delimeter`.

```
UT.delimitString(["bright", "world"], " ")

> "bright world"

UT.delimitString("I wandered lonely as an artichoke", ".")

> "I.wandered.lonely.as.an.artichoke"
```

<a name=makedictfromstring></a>
### [makeDictFromString(istr)](#menu)

[Code](https://github.com/ccdale/ccautils/blob/master/ccautils/utils.py#L64)

Constructs a dictionary from a string of parameters. Leading and trailing
whitespace is stripped.

`istr` should be in the form `someparam=somevalue,someotherparam=otherval`

```
UT.makeDictFromString("sparam=sval, soparam = soval")

> {"sparam": "sval", "soparam": "soval"}
```

<a name=askme></a>
### [askMe(q, default)](#menu)

[Code](https://github.com/ccdale/ccautils/blob/master/ccautils/utils.py#L89)

Requests input from the user.  Poses the question `q`. Returns the users
input or `default` if no input given.

```
UT.askMe("press 5, please", "8")

> press 5, please: 5
> 5
```

<a name=padstr></a>
### [padStr(xstr, xlen=2, pad=" ", padleft=True)](#menu)

[Code](https://github.com/ccdale/ccautils/blob/master/ccautils/utils.py#L101)

Returns `xstr` `pad`ded to the required length, either on the
left (`padleft` is True) or the right (`padleft` is False)

```
UT.padStr("23", 5, "0")

> "00023"
```

<a name=reducetime></a>
### [reduceTime(unit, secs)](#menu)

[Code](https://github.com/ccdale/ccautils/blob/master/ccautils/utils.py#L115)

Divides `secs` by `unit` returning a tuple of (`units`, `remainder`)

Raises a `ValueError` if `unit` is zero.

```
UT.reduceTime(3600, 3700)

> (1, 100)
```

<a name=displayvalue></a>
### [displayValue(val, label, zero=True)](#menu)

[Code](https://github.com/ccdale/ccautils/blob/master/ccautils/utils.py#L131)

Pluralises `label` if `val` > 1 or `val` is 0.

Will return an empty string if `val` == 0 and `zero` == True

```
UT.displayValue(12, "table")

> "12 tables"
```

<a name=secondsfromhms></a>
### [secondsFromHMS(shms)](#menu)

[Code](https://github.com/ccdale/ccautils/blob/master/ccautils/utils.py#L142)

converts HMS strings into integer seconds

```
UT.secondsFromHMS("01:01:23.43")
# 1 hour, 1 minute, 23 seconds + 0.43 second

> 3683
```

<a name=hms></a>
### [hms(secs, small=True, short=True, single=False)](#menu)

[Code](https://github.com/ccdale/ccautils/blob/master/ccautils/utils.py#L168)

Convert `secs` to days, hours, minutes and seconds

if `small` is True then only return the higher values if they are > zero

if `short` is True then the labels are their short form

if `single` is True then the labels are single letters

```
UT.hms(67)

> "1 min and 7 secs"

UT.hms(67, short=False)

> "1 minute and 7 seconds"

UT.hms(67, small=False, short=False)

> "0 days, 0 hours, 1 minute and 7 seconds"

secs = 86400 + 7200 + 300 + 34
UT.hms(secs, single=True)

> "1d 2h 5m 34s"
```

<a name=futils></a>
## [File Utilities](#headdd)

<a name=fusage></a>
### [Usage](#headdd)

```
import ccautils.fileutils as FT
```
[modeline]: # ( vim: set ft=markdown tw=74 fenc=utf-8 spell spl=en_gb mousemodel=popup: )
