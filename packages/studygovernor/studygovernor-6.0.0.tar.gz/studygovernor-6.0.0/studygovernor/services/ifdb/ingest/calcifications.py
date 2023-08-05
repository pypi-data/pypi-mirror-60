from .abstractingestionadapter import AbstractIngestionAdapter


class Calcifications(AbstractIngestionAdapter):
    _LABELS = ['Calcification Choroid Plexus', 'Calcification Falx Cerebri', 'Calcification Globus Pallidus']

    def get_labels(self, field_parser):
        return self._LABELS

    def get_name(self):
        return 'Calcifications'

    def do_ingestion(self, ifdb, field_parser, incidental_findings, label_mappings, experiment_id, generator_url):
        calcifications = self._recursive_field_finder(incidental_findings, 'if_calcifications')

        if calcifications is None or len(calcifications) == 0:
            return  # no calcifications found, stop ingestion


        # we currently support three types of calcification
        # let's map the specific fields in incidental_findings var to the correct labels
        calcification_types = {
            'if_other_choroid_plexus': self._LABELS[0],
            'if_other_falx_cerebri': self._LABELS[1],
            'if_other_globus_pallidus': self._LABELS[2]
        }

        for calcification_type in calcification_types.keys():
            if calcification_type in calcifications and calcifications[calcification_type] == True:
                label = label_mappings[calcification_types[calcification_type]]
                incidental_finding = ifdb.new_finding(experiment_id, label, generator_url)
