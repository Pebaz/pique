"""
http://www.1728.org/colrchr6.htm
"""

from pygments.style import Style
from pygments.token import *


class IcyKiss(Style):
    default_style = ''
    styles = {
        Name: '#b2b',
        String: '#7bd',
        Number: '#07d',
        Keyword: 'bold #b0b'
    }


class Python3(Style):
    default_style = ''
    styles = {
        Name: '#07c',
        String: '#fc4',
        Number: '#4cf',
        Keyword: 'bold #fc4'
    }


class Allovelle(Style):
    default_style = ''
    styles = {
        Name: '#f0a',
        #String: '#fff',
        Number: '#fc4',
        Keyword: 'bold #f4a'
    }


class Haelyon(Style):
    default_style = ''
    styles = {
        Name: '#39b',
        String: '#3ab',
        Number: '#f05',
        Keyword: 'bold #888'
    }


class Wing(Style):
    default_style = ''
    styles = {
        Name: '#fc1',
        String: '#bbb',
        #Number: '#fff',
        Keyword: 'bold #bbb'
    }


class Spire(Style):
    default_style = ''
    styles = {
        Name: '#bd2',
        String: '#fb1',
        Number: '#1bf',
        Keyword: 'bold #f05'
    }


class Cuttlefish(Style):
    default_style = ''
    styles = {
        Name: '#603',
        String: '#fc0',
        Number: '#fff',
        Keyword: 'bold #b07'
    }

THEMES = [
    Python3,
    IcyKiss,
    Spire,
    Wing,
    Cuttlefish
]
