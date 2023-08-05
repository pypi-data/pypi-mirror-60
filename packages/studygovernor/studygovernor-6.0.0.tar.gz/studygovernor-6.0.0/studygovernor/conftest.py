# Copyright 2017 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pathlib
import pytest

from . import create_app
from .models import db


@pytest.fixture(scope="session")
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    db_uri = 'sqlite:///:memory:'

    # create the app with common test config
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': db_uri,
        'SECRET_KEY': 'o8[nc2foeu2foe2ij',
        'SECURITY_PASSWORD_SALT': 'sgfms8-tcfm9de2nv'
    }, use_sentry=False)

    yield app


@pytest.fixture(scope="session")
def init_db(app):
    # create the database and load test data
    db.create_all(app=app)
    yield app


@pytest.fixture(scope="session")
def app_config(app, init_db):
    # Load the config file with initial setup
    config_file = pathlib.Path(__file__).parent / 'tests' / 'config' / 'test_config.json'
    from .util.helpers import load_config_file
    load_config_file(app, config_file, silent=True)

    yield app


@pytest.fixture(scope="session")
def workflow_test_data(app, init_db, app_config):
    # Load test workflow
    workflow_file = pathlib.Path(__file__).parent / 'tests' / 'test_workflow.yaml'

    # Make sure the workflow is loaded
    from .util.helpers import initialize_workflow
    initialize_workflow(workflow_file, app=app)

    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()