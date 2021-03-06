import logging
from uuid import UUID

from udata.core.dataset.models import get_resource
log = logging.getLogger(__name__)


def consume_message_resource_analysed(key, value):
    '''
    Reads a message and update the resource extras with analysis information, ex:
    report location, mime, filesize, etc.
    '''
    log.info("Consuming message analysed")
    resource = get_resource(UUID(key))
    if resource:
        # TODO: add extra logic here
        for entry in value['value']:
            if entry == 'location' and isinstance(value['value'][entry], dict):
                resource.extras['analysis:location'] = '/'.join([
                    value['value']['location']['url'].strip('/'),
                    value['value']['location']['bucket'],
                    value['value']['location']['key']])
            elif value['value'][entry] is not None:
                resource.extras[f'analysis:{entry}'] = value['value'][entry]
        resource.save()
    else:
        log.warn(f'No resource found for key {key}')


def consume_message_resource_stored(key, value):
    '''
    Reads a message and update the resource extras with the S3 stored location.
    '''
    log.info("Consuming message stored")
    resource = get_resource(UUID(key))
    if resource:
        resource.extras['store:location'] = '/'.join([
            value['value']['location']['netloc'].strip('/'),
            value['value']['location']['bucket'],
            value['value']['location']['key']])
        resource.save()
    else:
        log.warn(f'No resource found for key {key}')


def consume_message_resource_checked(key, value):
    '''
    Reads a message and update the resource extras with checked information, in particular:
    status, timeout, check date.
    '''
    log.info("Consuming message checked")
    resource = get_resource(UUID(key))
    if resource:
        if 'status' in value['value']:
            resource.extras['check:status'] = value['value']['status']
        if 'timeout' in value['value']:
            resource.extras['check:timeout'] = value['value']['timeout']
        if 'check_date' in value['meta']:
            resource.extras['check:check_date'] = value['meta']['check_date']
        resource.save()
    else:
        log.warn(f'No resource found for key {key}')
