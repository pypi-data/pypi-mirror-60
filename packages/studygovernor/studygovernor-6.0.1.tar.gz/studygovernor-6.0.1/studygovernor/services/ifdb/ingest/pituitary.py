from .abstractingestionadapter import AbstractIngestionAdapter


class Pituitary(AbstractIngestionAdapter):
    _LABELS = [
        'Pituitary Empty Sella', # 0
        'Pituitary Hemorrhage', # 1
        'Pituitary Macroadenoma',     # 2
        'Pituitary Microadenoma',  # 3
    ]

    def get_labels(self, field_parser):
        return self._LABELS

    def get_name(self):
        return 'Pituitary'

    def do_ingestion(self, ifdb, field_parser, incidental_findings, label_mappings, experiment_id, generator_url):
        findings = self._recursive_field_finder(incidental_findings, 'if_pituitary')

        if findings is None or len(findings) == 0:
            return  # no findings found, stop ingestion

        # list of fields, these are the actual findings
        # let's map the fields to the correct labels
        finding_types = {
            'if_other_empty_sella': self._LABELS[0],
            'if_other_hemorrhage': self._LABELS[1],
            'if_other_macroadenoma': self._LABELS[2],
            'if_other_microadenoma': self._LABELS[3]
        }

        for finding_type in finding_types.keys():
            if finding_type in findings and findings[finding_type] == True: # it's only a finding if the field contains value True
                label = label_mappings[finding_types[finding_type]]
                incidental_finding = ifdb.new_finding(experiment_id, label, generator_url)
