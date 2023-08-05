from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'example\.com', 'tests.urls.simple',
         name='without_www'),
    host(r'www\.example\.com', 'tests.urls.simple', name='www'),
    host(r'static', 'tests.urls.simple', name='static'),
    host(r'^s(?P<subdomain>\w+)', 'tests.urls.complex',
         name='with_view_kwargs'),
    host(r'wiki\.(?P<domain>\w+)', 'tests.urls.simple',
         callback='django_hosts.callbacks.host_site', name='with_callback'),
    host(r'admin\.(?P<domain>\w+)', 'tests.urls.simple',
         callback='django_hosts.callbacks.cached_host_site',
         name='with_cached_callback'),
    host(r'(?P<username>\w+)', 'tests.urls.simple',
         name='with_kwargs'),
    host(r'(\w+)', 'tests.urls.simple', name='with_args'),
    host(r'scheme', 'tests.urls.simple', name='scheme',
         scheme='https://'),
    host(r'port', 'tests.urls.simple', name='port',
         port='12345'),
    host(r'port-tag', 'tests.urls.simple', name='port-tag',
         port='12345'),
)
