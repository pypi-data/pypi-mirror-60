from .abstractingestionadapter import AbstractIngestionAdapter
from pprint import pprint


class Tumors(AbstractIngestionAdapter):
    def get_labels(self, field_parser):
        self._labels = ['Tumor {}'.format(tumor_type) for tumor_type in field_parser.find_field_options('if_tumor_type')]
        return self._labels

    def get_name(self):
        return 'Tumors'

    def do_ingestion(self, ifdb, field_parser, incidental_findings, label_mappings, experiment_id, generator_url):
        tumors = self._recursive_field_finder(incidental_findings, 'tumors')

        if tumors is None or len(tumors) == 0:
            return  # no tumors found, stop ingestion

        # loop trough all tumors and insert incidental finding
        for tumor in tumors:
            label_id = self.get_tumor_label(tumor, label_mappings)

            if label_id is None:
                print('WARN: Could not map tumor, field "if_tumor_type" not present')
                pprint(tumor)
                continue

            incidental_finding = ifdb.new_finding(experiment_id, label_id, generator_url)
            finding_id = incidental_finding['finding_id']
            self._auto_properties(tumor, field_parser, ifdb, finding_id)


    def get_tumor_label(self, tumor, label_mappings):
        if 'if_tumor_type' not in tumor:
            return None

        tumor_type = tumor['if_tumor_type']

        if tumor_type is None or len(tumor_type) == 0:
            return None

        label = 'Tumor ' + tumor_type
        if label in label_mappings:
            return label_mappings[label]

        return None
