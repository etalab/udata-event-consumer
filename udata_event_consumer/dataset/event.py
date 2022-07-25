import logging
from uuid import UUID

from udata.core.dataset.models import get_resource
log = logging.getLogger(__name__)


def concat_location(location: dict) -> str:
    '''
    Return an url from an object storage location object.
    Input example:
    {
        "url": "http://minio:9000/",
        "bucket": "udata",
        "key": "data/71cacba9-4ffd-4ea8-bc3e-694425ddf006"
    }
    would return the following string:
    "http://minio:9000/udata/data/71cacba9-4ffd-4ea8-bc3e-694425ddf006"
    '''
    return '/'.join([location['url'].strip('/'), location['bucket'], location['key']])


def consume_message_resource_analysed(key: str, message: dict) -> None:
    '''
    Reads a message and update the resource extras with analysis information, ex:
    report location, mime, filesize, etc.
    '''
    log.info('Consuming message analysed')
    resource = get_resource(UUID(key))
    value = message['value']
    if resource:
        if message['service'] == 'udata-hydra':
            resource.extras['analysis:error'] = value['error']
            resource.extras['analysis:filesize'] = value['filesize']
            resource.extras['analysis:mime'] = value['mime']
        elif message['service'] == 'detective':
            resource.extras['analysis:data_location'] = concat_location(value['data_location'])
            resource.extras['analysis:report_location'] = concat_location(value['report_location'])
            resource.extras['analysis:schema_location'] = concat_location(value['schema_location'])
            resource.extras['analysis:encoding'] = value['encoding']
            resource.extras['analysis:delimiter'] = value['delimiter']
        else:
            log.warn(f'Unexpected service for resource analysed topic for key {key}')
        resource.save()
    else:
        log.warn(f'No resource found for key {key}')


def consume_message_resource_stored(key: str, message: dict) -> None:
    '''
    Reads a message and update the resource extras with the S3 stored location.
    '''
    log.info('Consuming message stored')
    resource = get_resource(UUID(key))
    if resource:
        resource.extras['store:location'] = concat_location(message['value']['data_location'])
        resource.save()
    else:
        log.warn(f'No resource found for key {key}')


def consume_message_resource_checked(key: str, message: dict) -> None:
    '''
    Reads a message and update the resource extras with checked information, in particular:
    status, timeout, check date.
    '''
    log.info('Consuming message checked')
    resource = get_resource(UUID(key))
    value = message['value']
    if resource:
        resource.extras['check:status'] = value['status']
        resource.extras['check:timeout'] = value['timeout']
        resource.extras['check:check_date'] = value['check_date']
        resource.save()
    else:
        log.warn(f'No resource found for key {key}')
