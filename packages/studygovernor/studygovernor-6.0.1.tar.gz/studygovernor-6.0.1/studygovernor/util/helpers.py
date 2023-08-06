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

import os
import yaml

from flask_security import SQLAlchemyUserDatastore
from flask_security.utils import hash_password

from .. import models
from .. import exceptions


def load_config_file(app, file_path, silent=False):
    file_path = str(file_path)

    with app.app_context():
        db = models.db

        user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
        if not os.path.isfile(file_path):
            db.session.rollback()
            raise ValueError(f"The file ({file_path}) does not exist")

        basedir = os.path.dirname(os.path.abspath(file_path))
        with open(file_path) as fh:
            config = yaml.safe_load(fh)

        if 'roles' in config:
            if not silent:
                print("\n Adding Roles:")
            roles = {}
            for role in config["roles"]:
                roles[role['name']] = user_datastore.create_role(**role)
                if not silent:
                    print(f"{roles[role['name']]} {role}")
            db.session.commit()

        if 'users' in config:
            if not silent:
                print("\nAdding users:")
            for user in config['users']:
                user['password'] = hash_password(user['password'])
                db_user = user_datastore.create_user(**user)
                if not silent:
                    print(f"Adding {db_user}")
            db.session.commit()

        if not silent:
            print("\nCommitting to the database ...")
        db.session.commit()
        if not silent:
            print("[ DONE ]")


def get_object_from_arg(id, model, model_name=None, skip_id=False, allow_none=False):
    data = None

    if isinstance(id, model):
        return id

    if id is not None:
        # If we have a URI/path we just want the last part
        if isinstance(id, str) and '/' in id:
            id = id.rsplit('/', 1)[1]

        # For id try to cast to an int
        if not skip_id:
            try:
                id = int(id)
            except (TypeError, ValueError) as e:
                pass

        if isinstance(id, int):
            data = model.query.filter(model.id == id).one_or_none()
        elif model_name is not None:
            data = model.query.filter(model_name == id).one_or_none()

    if data is None and not allow_none:
        raise exceptions.CouldNotFindResourceError(id, model)

    return data


def initialize_workflow(workflow, app, verbose=False, force=True):
    from pathlib import Path
    from .. import models

    if isinstance(workflow, (str, Path)):
        try:
            with open(workflow) as fh:
                workflow_definition = yaml.safe_load(fh)
        except IOError as experiment:
            print("IOError: {}".format(experiment))
            print("Please specify a valid YAML file.")
            return
    else:
        workflow_definition = workflow

    if verbose:
        def do_print(message):
            print(message)
    else:
        def do_print(message):
            pass

    with app.app_context():
        db = models.db
        db.session.query(models.Scantype).delete()
        db.session.query(models.ExternalSystem).delete()
        db.session.query(models.Transition).delete()
        db.session.query(models.State).delete()

        do_print("\n * Importing states:")
        states = dict()
        for i, state in enumerate(workflow_definition['states']):
            callback = state['callback']

            # Allow callback to be defined as nested JSON rather than a string containing escaped JSON
            if not isinstance(callback, str):
                callback = yaml.safe_dump(callback)

            states[state['label']] = models.State(id=i+1, label=state['label'], lifespan=state['lifespan'], callback=callback, freetext=state['freetext'])
            db.session.add(states[state['label']])
            do_print("\t - {}".format(state['label']))

        do_print("\n * Importing transitions:")
        for i, transition in enumerate(workflow_definition['transitions']):
            #TODO add conditions
            db.session.add(models.Transition(id=i+1, source_state=states[transition['source']], destination_state=states[transition['destination']]))
            do_print("\t - {} -> {}".format(transition['source'], transition['destination']))

        do_print("\n * Importing external_systems:")
        for i, experiment in enumerate(workflow_definition['external_systems']):
            db.session.add(models.ExternalSystem(id=i+1, system_name=experiment['system_name'], url=experiment['url']))
            do_print("\t - {}".format(experiment['system_name']))

        do_print("\n * Importing scantypes:")
        for i, scan_type in enumerate(workflow_definition['scantypes']):
            db.session.add(models.Scantype(id=i+1, modality=scan_type['modality'], protocol=scan_type['protocol']))
            do_print("\t - {} {}".format(scan_type['modality'], scan_type['protocol']))

        doit = False
        if not force:
            doit = input("Are you sure you want to commit this to '{}' [yes/no]: ".format(app.config['SQLALCHEMY_DATABASE_URI'].rsplit('/', 1)[1])) == 'yes'

        if doit or force:
            db.session.commit()
            do_print("\n * Committed to the database.")
        else:
            db.session.rollback()
            do_print("\n * Cancelled the initialisation of the workflows.")
