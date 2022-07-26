import pytest

from udata.core.dataset.factories import DatasetFactory, ResourceFactory

from udata_event_consumer.consumer import EventConsumerSingleton
import udata_event_consumer  # noqa


@pytest.mark.usefixtures('event_consumer_app')
class ConsumerTest:
    def test_consume_resource_stored_event(self):
        dataset = DatasetFactory()
        resource = ResourceFactory()
        dataset.add_resource(resource)

        data = {
            'service': 'udata-hydra',
            'value': {
                'data_location': {
                    'netloc': 'http://localhost:9000/',
                    'bucket': 'bucket',
                    'key': 'folder/path.csv'
                }
            },
            'meta': {
                'dataset_id': str(dataset.id),
                'message_type': 'resource.stored'
            }
        }

        event_consumer = EventConsumerSingleton.get_instance()
        event_consumer.route_messages(str(resource.id), data)

        dataset.reload()
        resource = dataset.resources[0]
        assert set(resource.extras.keys()) == {'store:data_location'}
        assert resource.extras['store:data_location'] == 'http://localhost:9000/bucket/folder/path.csv'

    def test_consume_resource_analysed_csvdetective_event(self):
        dataset = DatasetFactory()
        resource = ResourceFactory()
        dataset.add_resource(resource)

        data = {
            'service': 'csvdetective',
            'value': {
                'report_location': {
                    'netloc': 'http://localhost:9000/',
                    'bucket': 'bucket',
                    'key': 'report/path.json'
                },
                'tableschema_location': {
                    'netloc': 'http://localhost:9000/',
                    'bucket': 'bucket',
                    'key': 'schemas/path.json'
                },
                'delimiter': ';',
                'encoding': 'ASCII'
            },
            'meta': {
                'dataset_id': str(dataset.id),
                'message_type': 'resource.analysed'
            }
        }

        event_consumer = EventConsumerSingleton.get_instance()
        event_consumer.route_messages(str(resource.id), data)

        dataset.reload()
        resource = dataset.resources[0]
        assert set(resource.extras.keys()) == {
            'analysis:report_location', 'analysis:tableschema_location', 'analysis:delimiter', 'analysis:encoding'
        }
        assert resource.extras['analysis:report_location'] == 'http://localhost:9000/bucket/report/path.json'
        assert resource.extras['analysis:tableschema_location'] == 'http://localhost:9000/bucket/schemas/path.json'
        assert resource.extras['analysis:delimiter'] == ';'
        assert resource.extras['analysis:encoding'] == 'ASCII'

    def test_consume_resource_analysed_hydra_event(self):
        dataset = DatasetFactory()
        resource = ResourceFactory()
        dataset.add_resource(resource)

        data = {
            'service': 'udata-hydra',
            'value': {
                'mime': 'text/plain',
                'resource_url': 'https://static.data.gouv.fr/resources/path.csv',
                'filesize': 154612
            },
            'meta': {
                'dataset_id': str(dataset.id),
                'message_type': 'resource.analysed'
            }
        }

        event_consumer = EventConsumerSingleton.get_instance()
        event_consumer.route_messages(str(resource.id), data)

        dataset.reload()
        resource = dataset.resources[0]
        assert set(resource.extras.keys()) == {'analysis:mime', 'analysis:filesize'}
        assert resource.extras['analysis:mime'] == 'text/plain'
        assert resource.extras['analysis:filesize'] == 154612

    def test_consume_resource_analysed_hydra_event_with_error(self):
        dataset = DatasetFactory()
        resource = ResourceFactory()
        dataset.add_resource(resource)

        data = {
            'service': 'udata-hydra',
            'value': {
                'resource_url': 'https://static.data.gouv.fr/resources/path.csv',
                'filesize': None,
                'error': 'File too large to download'
            },
            'meta': {
                'dataset_id': str(dataset.id),
                'message_type': 'resource.analysed'
            }
        }

        event_consumer = EventConsumerSingleton.get_instance()
        event_consumer.route_messages(str(resource.id), data)

        dataset.reload()
        resource = dataset.resources[0]
        assert set(resource.extras.keys()) == {'analysis:error'}
        assert resource.extras['analysis:error'] == 'File too large to download'

    def test_consume_resource_checked(self):
        dataset = DatasetFactory()
        resource = ResourceFactory()
        dataset.add_resource(resource)

        data = {
            'service': 'udata-hydra',
            'value': {
                'url': 'https://www.data.gouv.fr/fr/datasets/r/79b5cac4-4957-486b-bbda-322d80868224',
                'domain': 'www.data.gouv.fr',
                'status': 200,
                'headers': {
                    'server': 'nginx',
                    'date': 'Mon, 02 May 2022 09:58:47 GMT',
                    'content-type': 'text/plain',
                    '...': '...',
                    'access-control-allow-origin': '*',
                    'access-control-allow-methods': 'GET, OPTIONS',
                    'content-encoding': 'gzip',
                },
                'timeout': False,
                'response_time': 0.16390085220336914,
                'check_date': '2020-02-02 20:20:20.202020'
            },
            'meta': {
                'dataset_id': str(dataset.id),
                'message_type': 'event-update',
            }
        }

        event_consumer = EventConsumerSingleton.get_instance()
        event_consumer.route_messages(str(resource.id), data)

        dataset.reload()
        resource = dataset.resources[0]
        assert set(resource.extras.keys()) == {'check:check_date', 'check:status',
                                               'check:timeout'}
        assert resource.extras['check:status'] == 200
        assert resource.extras['check:timeout'] is False
        assert resource.extras['check:check_date'] == '2020-02-02 20:20:20.202020'
