from .abstractingestionadapter import AbstractIngestionAdapter


class Aneurysm(AbstractIngestionAdapter):
    _LABELS = ['Aneurysm']

    def get_labels(self, field_parser):
        return self._LABELS

    def get_name(self):
        return 'Aneurysms'

    def do_ingestion(self, ifdb, field_parser, incidental_findings, label_mappings, experiment_id, generator_url):
        self._auto_findings(incidental_findings, 'aneurysms', field_parser, ifdb, label_mappings[self._LABELS[0]], experiment_id, generator_url)