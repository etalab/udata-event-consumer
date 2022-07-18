'''
event-consumer

A udata plugin to consume kafka events
'''

import os

from .consumer import EventConsumerSingleton
from .commands import consume  # noqa


tag = os.environ.get('CIRCLE_TAG')
build_num = os.environ.get('CIRCLE_BUILD_NUM')

__version__ = '0.1.0.dev' + (str(build_num) if not tag and build_num else '')
__description__ = 'A plugin to consume events'


def init_app(app):
    event_consumer = EventConsumerSingleton.get_instance()

    from .dataset.event import (
        consume_message_resource_analysed,
        consume_message_resource_stored,
        consume_message_resource_checked
    )
    # Register consume functions
    event_consumer.register(
        topics=[f'{app.config["UDATA_INSTANCE_NAME"]}.resource.analysed'],
        message_types=['resource.analysed'],
        function=consume_message_resource_analysed
    )
    event_consumer.register(
        topics=[f'{app.config["UDATA_INSTANCE_NAME"]}.resource.stored'],
        message_types=['resource.stored'],
        function=consume_message_resource_stored
    )
    event_consumer.register(
        topics=[f'{app.config["UDATA_INSTANCE_NAME"]}.resource.checked'],
        message_types=['event-update', 'initialization', 'regular-update'],
        function=consume_message_resource_checked
    )
