# URL Parser
![PyPI - Downloads](https://img.shields.io/pypi/dm/url-parser?style=plastic)
![PyPI - Format](https://img.shields.io/pypi/format/url-parser?style=plastic)
![PyPI - Status](https://img.shields.io/pypi/status/url-parser?style=plastic)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/url-parser?style=plastic)
##### supports secondary top domain (like: co.uk, .parliament.uk, .gov.au)

A small yet nice package to help you parse all types of url`s and return the parsed url with group name.

### Installation
```
pip install url-parser
```

### Usage

```
from url_parser import parse_url


parsed_url = parse_url('https://open.prospecta.app')

print(pared_url)
>>> {'http': 'https://', 'www': None, 'sub_domain': 'open.', 'domain': 'prospecta', 'top_domain': 'app', 'dir': 'app'}
```

### keywords

You can call the package with specific keywords to return the part of the url you  want.

| keyword | result |
| ------ | ------ |
| ['http'] | Returns: http/https or None |
| ['www'] | Returns: www or None |
| ['sub_domain'] | Returns: sub-domain or None |
| ['domain'] | Returns: domain or None |
| ['top_domain'] | Returns: top-domain or None |
| ['dir'] | Returns: directory or None |

### Usage with keywords

```
from url_parser import parse_url


parsed_url = parse_url('https://open.prospecta.app')

http = parsed_url['http']
sub_domain = parsed_url['sub_domain']
domain = parsed_url['domain']
top_domain = parsed_url['top_domain']

print(http)
>>> https://

print(sub_domain)
>>> open

print(domain)
>>> prospecta

print(top_domain)
>>> .app
```