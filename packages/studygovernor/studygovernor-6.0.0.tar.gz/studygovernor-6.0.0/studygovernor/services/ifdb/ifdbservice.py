from pprint import pformat

from . import ingest
from .ingest.ifdbclient import IfdbV1
from .ingest.fieldparser import FieldParser
from studygovernor.services.ifdb.exceptions import InvalidParameterException, NoSyncableDataException, CannotReachIfdbException


def ingest_json(incidental_findings, template_data, ifdb_url, task_template, subject_study_id, subject_generator_url, experiment_date, finding_generator_url):
    """
    Ingest json to ifdb

    :raises InvalidParameterException, NoSyncableDataException, CannotReachIfdbException

    :param experiment_date: ISO 8601 datestring
    :param subject_generator_url: url to subject generator
    :param subject_study_id: study id of subject (e.g. ergoid)
    :param json_file_path: path to the json file
    :param ifdb_url: url to the ifdb server
    :param task_template: template used for findings
    :return: No return value
    """

    ifdb = IfdbV1(ifdb_url)

    if not ifdb.ping():
        raise CannotReachIfdbException('Cannot reach ifdb on url: {}'.format(ifdb_url))

    field_parser = FieldParser(template_data=template_data)

    label_mappings = {}

    if not 'tabs' in incidental_findings:
        # no data to sync
        raise NoSyncableDataException('Has the json datastructure changed? Key "tabs" not found in: {}'.format(json_file_path))

    tabs = incidental_findings['tabs']  # slightly trim down incidental_findings var so that recursive lookups are slightly faster

    # put subject
    subject = ifdb.put_subject(study_id=subject_study_id, generator_url=subject_generator_url)

    if subject is None or 'subject_id' not in subject:
        raise InvalidParameterException('Could not put subject: {} {}, api result: {}'.format(subject_study_id, subject_generator_url, pformat(subject)))

    # put experiment
    experiment = ifdb.put_experiment(subject_id=subject['subject_id'], experiment_date=experiment_date, task_template=task_template)

    if experiment is None or 'experiment_id' not in experiment:
        raise InvalidParameterException('Could not put experiment {} {}, api result: {}'.format(subject['subject_id'], experiment_date, pformat(experiment)))

    ifdb.delete_findings_for_experiment_by_template(experiment['experiment_id'], task_template)

    for IngestionAdapter in ingest.ingestion_adapters:
        adapter = IngestionAdapter()
        adapter_labels = adapter.get_labels(field_parser)

        # first we synchronize the adapters labels to ifdb
        for label in adapter_labels:
            label = label.strip()
            new_label = ifdb.put_label(label)
            label_mappings[label] = new_label['label_id']

        # second we do the actual ingestion
        adapter.do_ingestion(ifdb, field_parser, tabs, label_mappings, experiment['experiment_id'], finding_generator_url)
