from .abstractingestionadapter import AbstractIngestionAdapter


class Microbleeds(AbstractIngestionAdapter):
    _LABELS = ['Cerebral Microbleed']

    def get_labels(self, field_parser):
        return self._LABELS

    def get_name(self):
        return 'Cerebral Microbleed'

    def do_ingestion(self, ifdb, field_parser, incidental_findings, label_mappings, experiment_id, generator_url):
        self._auto_findings(incidental_findings, 'microbleeds', field_parser, ifdb, label_mappings[self._LABELS[0]], experiment_id, generator_url)
