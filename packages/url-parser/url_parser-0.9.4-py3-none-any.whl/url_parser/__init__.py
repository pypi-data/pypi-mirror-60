import re


def parse_url(item):
    http = None
    www = None
    sub_domain = None
    domain = None
    top_domain = None
    sub_dir = None
    regex = r"(?P<http>http\:\/\/|https\:\/\/|)(?P<www>[www.]*(?=[a-zA-Z0-9-]+\.[a-zA-Z0-9-]+))" \
            r"(?P<sub_domain>(?=[a-zA-Z0-9-]+\.[a-zA-Z0-9]{2,4}|[a-zA-Z0-9-]+\.[a-zA-Z0-9]{2,4}\/.*)" \
            r"[a-zA-Z0-9-]*\.)?(?P<domain>(?=[a-zA-Z0-9]{2,}|[a-zA-Z0-9]{2,4}\/.*)[a-zA-Z0-9-]+(?=\.)" \
            r")\.(?P<top_domain>(?<=\.)[a-zA-Z0-9]{2,4}(?=$|\/))(?P<dir>\/.*(?=$|\/))?"
    matches = re.finditer(regex, item)
    for match in matches:
        http = match.group('http')
        if http == '':
            http = None
        www = match.group('www')
        if www == '':
            www = None
        if www != None:
            if '.' in www:
                www = www.replace('.', '')
        sub_domain = match.group('sub_domain')
        if sub_domain == '':
            sub_domain = None
        if sub_domain != None:
            if '.' in sub_domain:
                sub_domain = sub_domain.replace('.', '')
        domain = match.group('domain')
        top_domain = match.group('top_domain')
        sub_dir = match.group('dir')
        if sub_dir == '':
            sub_dir = None

    return {'http': http, 'www': www, 'sub_domain': sub_domain, 'domain': domain, 'top_domain': top_domain, 'dir': sub_dir}