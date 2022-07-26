import logging
from uuid import UUID

from udata.core.dataset.models import get_resource
log = logging.getLogger(__name__)


def concat_location(location: dict) -> str:
    '''
    Return an url from an object storage location object.
    Input example:
    {
        "netloc": "http://minio:9000/",
        "bucket": "udata",
        "key": "data/71cacba9-4ffd-4ea8-bc3e-694425ddf006"
    }
    would return the following string:
    "http://minio:9000/udata/data/71cacba9-4ffd-4ea8-bc3e-694425ddf006"
    '''
    return '/'.join([location['netloc'].strip('/'), location['bucket'], location['key']])


def consume_message_resource_analysed(key: str, message: dict) -> None:
    '''
    Reads a message and update the resource extras with analysis information, ex:
    report location, mime, filesize, etc.
    '''
    log.info('Consuming message analysed')
    resource = get_resource(UUID(key))
    value = message['value']
    service = message["service"]
    if resource:
        if service == 'udata-hydra':
            for key in ['error', 'filesize', 'mime']:
                if value.get(key, None) is not None:
                    resource.extras[f'analysis:{key}'] = value[key]
        elif service == 'csvdetective':
            resource.extras['analysis:report_location'] = concat_location(value['report_location'])
            resource.extras['analysis:tableschema_location'] = concat_location(value['tableschema_location'])
            resource.extras['analysis:encoding'] = value['encoding']
            resource.extras['analysis:delimiter'] = value['delimiter']
        else:
            log.warn(f'Unexpected service {service} for resource analysed topic for key {key}')
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
        resource.extras['store:data_location'] = concat_location(message['value']['data_location'])
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
        for key in ['status', 'timeout', 'check_date']:
            if value.get(key, None) is not None:
                resource.extras[f'check:{key}'] = value[key]
        resource.save()
    else:
        log.warn(f'No resource found for key {key}')
