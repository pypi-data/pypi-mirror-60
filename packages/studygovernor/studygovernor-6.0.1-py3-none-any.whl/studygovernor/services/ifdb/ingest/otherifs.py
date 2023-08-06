from .abstractingestionadapter import AbstractIngestionAdapter


class OtherIfs(AbstractIngestionAdapter):
    _LABELS = [
        'Carotid OCCL L', # 0
        'Carotid OCCL R', # 1
        'Cavum Sept',     # 2
        'Fibrous Dyspl',  # 3
        'Hyperostosis',   # 4
        'Ectopic GM',     # 5
        'Kele Cerebellum',# 6
        'Kele Cerebrum',  # 7
        'Mastoid Fluid',  # 8
        'SDH',            # 9
        'AVM',            # 10
        'DVA',            # 11
        'PTA',            # 12
        'Dural AV',       # 13
        'Sup Siderosis'   # 14
    ]

    def get_labels(self, field_parser):
        return self._LABELS

    def get_name(self):
        return 'Other Ifs'

    def do_ingestion(self, ifdb, field_parser, incidental_findings, label_mappings, experiment_id, generator_url):
        # list of main fields where we should look for subfields
        main_fields = ['if_fifth', 'if_fourth', 'if_second']

        # list of sub-fields, these are the actual findings
        # let's map the sub-fields in incidental_findings var to the correct labels
        finding_types = {
            'if_other_carotid_occl_l': self._LABELS[0],
            'if_other_carotid_occl_r': self._LABELS[1],
            'if_other_cavum_sept': self._LABELS[2],
            'if_other_fibrous_dyspl': self._LABELS[3],
            'if_other_hyperostosis': self._LABELS[4],
            'if_other_ectopic_gm': self._LABELS[5],
            'if_other_kele_cerebellum': self._LABELS[6],
            'if_other_kele_cerebrum': self._LABELS[7],
            'if_other_mastoid_fluid': self._LABELS[8],
            'if_other_sdh': self._LABELS[9],
            'if_other_AVM': self._LABELS[10],
            'if_other_DVA': self._LABELS[11],
            'if_other_PTA': self._LABELS[12],
            'if_other_dural_av': self._LABELS[13],
            'if_other_sup_siderosis': self._LABELS[14]
        }

        for main_field in main_fields:
            findings = self._recursive_field_finder(incidental_findings, main_field)

            if findings is None or len(findings) == 0:
                continue  # no findings found, continue to next main_field

            for finding_type in finding_types.keys():
                if finding_type in findings and findings[finding_type] == True:
                    label = label_mappings[finding_types[finding_type]]
                    incidental_finding = ifdb.new_finding(experiment_id, label, generator_url)
