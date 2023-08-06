import re


def parse_url(item):
    http = None
    www = None
    sub_domain = None
    domain = None
    top_domain = None
    sub_dir = None
    url_args = None
    top_top_domain = ''

    if 'www.' in item:
        if item.count('.') == 4:
            top_top_domain = '.' + item.split('.')[4]
            item = item.replace(top_top_domain, '')

    if 'www.' not in item:
        if item.count('.') == 3:
            top_top_domain = '.' + item.split('.')[3]
            item = item.replace(top_top_domain, '')

    regex = r"(?P<http>http\:\/\/|https\:\/\/|)" \
            r"(?P<www>[www.]*(?=[a-zA-Z0-9-]+\.[a-zA-Z0-9-]+))" \
            r"(?P<sub_domain>(?=[a-zA-Z0-9-]+\.[a-zA-Z0-9]{2,}|[a-zA-Z0-9-]+\.[a-zA-Z0-9]{2,}\/.*)[a-zA-Z0-9-]*\.)?" \
            r"(?P<domain>(?=[a-zA-Z0-9]{2,}|[a-zA-Z0-9]{2,}\/.*)[a-zA-Z0-9-]+(?=\.))\." \
            r"(?P<top_domain>(?<=\.)[a-zA-Z0-9]{2,}(?=$|\/|\?))" \
            r"(?P<dir>\/[a-zA-Z0-9-_]*(?=$|\/|\?))*" \
            r"(?P<args>\?.*(?=$))*"

    matches = re.finditer(regex, item)
    for match in matches:
        http = match.group('http')
        if http == '':
            http = None

        www = match.group('www')
        if www == '':
            www = None
        if www is not None:
            if '.' in www:
                www = www.replace('.', '')

        sub_domain = match.group('sub_domain')
        if sub_domain == '':
            sub_domain = None
        if sub_domain is not None:
            if '.' in sub_domain:
                sub_domain = sub_domain.replace('.', '')

        domain = match.group('domain')
        top_domain = match.group('top_domain') + top_top_domain

        sub_dir = match.group('dir')
        if sub_dir == '':
            sub_dir = None
        if sub_dir is not None:
            sub_dir = sub_dir.lstrip('/')
            sub_dir = sub_dir.split('/')

        url_args = match.group('args')
        if url_args == '':
            url_args = None
        if url_args is not None:
            url_args = url_args.lstrip('?')
            url_args = url_args.split('&')

    return {'http': http, 'www': www, 'sub_domain': sub_domain, 'domain': domain, 'top_domain': top_domain, 'dir': sub_dir, 'args': url_args}


print(parse_url('https://open.prospecta.app/my_user_login?user=url-parser&password=H3ll0'))
