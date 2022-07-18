import pytest

import udata_event_consumer


@pytest.fixture
def event_consumer_app(app):
    udata_event_consumer.init_app(app)
    yield app
