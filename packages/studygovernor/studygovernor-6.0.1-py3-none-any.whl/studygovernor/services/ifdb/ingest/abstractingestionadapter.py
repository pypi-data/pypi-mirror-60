from abc import ABCMeta, abstractmethod
import json

class AbstractIngestionAdapter(metaclass=ABCMeta):
    @abstractmethod
    def get_labels(self, field_parser):
        pass

    @abstractmethod
    def do_ingestion(self, ifdb, field_parser, incidental_findings, label_mappings, experiment_id, finding_generator_url):
        pass

    @abstractmethod
    def get_name(self):
        pass

    def _recursive_field_finder(self, obj, field_name):
        if not isinstance(obj, dict):
            return None

        if field_name in obj:
            return obj[field_name]

        for field in obj.keys():
            val = self._recursive_field_finder(obj[field], field_name)

            if val is not None:
                return val

        return None

    def _auto_findings(self, incidental_findings, finding_root_field, field_parser, ifdb, label_id, experiment_id, generator_url):
        findings = self._recursive_field_finder(incidental_findings, finding_root_field)

        if findings is None or len(findings) == 0:
            return  # no incidental findings found, stop ingestion

        # loop trough all and insert incidental finding
        for finding in findings:
            incidental_finding = ifdb.new_finding(experiment_id, label_id, generator_url)
            if 'finding_id' not in incidental_finding:
                from pprint import pprint
                pprint(incidental_finding)
                raise Exception('Errored out!')
            finding_id = incidental_finding['finding_id']
            self._auto_properties(finding, field_parser, ifdb, finding_id)

    def _auto_properties(self, obj, field_parser, ifdb, finding_id):
        properties = self._property_extractor(obj, field_parser)

        for property in properties:
            ifdb.put_property(property, json.dumps(properties[property]), finding_id)

    def _property_extractor(self, obj, field_parser):
        properties_output = {}
        for field_name in obj:
            description = field_parser.find_field_description(field_name)

            if description is None or 'control' not in description:
                print('WARN: Could not find field description for field {}'.format(field_name))
                continue

            control = description['control'].strip().lower()

            if control in ['numberedit', 'combobox', 'markeredit']:
                properties_output[field_name] = obj[field_name]
            elif control == 'textbox' and len(obj[field_name].strip()) > 0:
                properties_output[field_name] = obj[field_name].strip()

        return properties_output
