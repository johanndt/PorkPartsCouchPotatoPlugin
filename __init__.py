from .main import TehConnection

def autoload():
    return TehConnection()

config = [{
    'name': 'tehconnection',
    'groups': [
        {
            'tab': 'searcher',
            'list': 'torrent_providers',
            'name': 'TehConnection',
            'description': 'See <a href="https://tehconnection.eu/">TehConnection</a>',
            'wizard': True,
            'icon': 'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAABe0lEQVQ4y3XTvWsVQRQF8N/uSxQJGiJi2EqtTKesQbSwEbQX0UILC8XGwsImjZWdSZkmkqQU/AsEDfgBVsII2gt2gkHQQk3i201zJ0weyYFlmdl77pxz9k7Vtq1AHc//vJFSAkUNDNCjgyo+DmKjxzhmcAkTQdrCR3zCn6JRNxanDtHgPu7glL2xjhdYwhfUWcEtLGIqCn/gNb6GquO4ihNx4Aae4skYFvAoiG8wj3f4G+SMAziLh7iBx7hQYw3f8QCX8TJ8HsJ0WDuMzcjhNq7hG1azhQn8iyxORxbXg9zjdzR+hg+ocBAbg6Zp6vgDQ9wM+RcxGel3OIIzuBt23mZ7mZy9rkdAr3AlFEzjPFbC2ucil64qBqWKRg1+Ff+7HKBJ/CwHrWxQKqqj4TDeVbHONTuEEl0xlUfxHO9xLsiDkryjIKMY6yGWo3gNc5iNdZVS6vdTMIq+PHEvVKMbbdvmMI9F8idxL4aoTil1+zYYubZZ4a4rnr1nbAOC0myw9QGJWAAAAABJRU5ErkJggg==',
            'options': [
                {
                    'name': 'enabled',
                    'type': 'enabler',
                    'default': False,
                },
                {
                    'name': 'username',
                    'default': '',
                },
                {
                    'name': 'password',
                    'default': '',
                    'type': 'password',
                },
                {
                    'name': 'seed_ratio',
                    'label': 'Seed ratio',
                    'type': 'float',
                    'default': 1,
                    'description': 'Will not be (re)moved until this seed ratio is met.',
                },
                {
                    'name': 'seed_time',
                    'label': 'Seed time',
                    'type': 'int',
                    'default': 96,
                    'description': 'Will not be (re)moved until this seed time (in hours) is met.',
                },
                                {
                    'name': 'only_freeleech',
                    'label': 'Freeleech',
                    'default': False,
                    'type': 'bool',
                    'description': 'Only search for [FreeLeech] torrents.',
                },
                {
                    'name': 'only_verified',
                    'label': 'Verified',
                    'default': False,
                    'type': 'bool',
                    'description': 'Only search for verified [Quality Encode] torrents.',
                },
                {
                    'name': 'extra_score',
                    'advanced': True,
                    'label': 'Extra Score',
                    'type': 'int',
                    'default': 20,
                    'description': 'Starting score for each release found via this provider.',
                }
            ],
        },
    ],
}]
