'''
event-consumer

A udata plugin to consume kafka events
'''

import os

tag = os.environ.get('CIRCLE_TAG')
build_num = os.environ.get('CIRCLE_BUILD_NUM')

__version__ = '0.1.0.dev' + (str(build_num) if not tag and build_num else '0')
__description__ = 'A udata plugin to consume kafka events'


def init_app(app):
    # Do whatever you want to initialize your plugin
    pass
