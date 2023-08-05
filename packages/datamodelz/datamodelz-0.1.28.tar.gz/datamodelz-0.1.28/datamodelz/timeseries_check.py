import logging

from datamodelz.error import Error

from . import rule
from .timeseries_metadata import TimeseriesMetadataField
from .data_list import DataList
from .field import Field


class TimeseriesCheck(Field):
    def __init__(self):
        """
        :param metadata_names:
        :param rules: list of Rule objects
        """
        super().__init__()
        self.name = "Timeseries Check"
        self.value = {}

        self.metadata = TimeseriesMetadataField()
        self.data = DataList()
        self.company = ""  # TODO
        self.reference = ""  # TODO
        self.api_call = ""  # TODO
        self.fields = [self.metadata, self.data]  # will add fields when needed for use case
        self.rules = [rule.has_field(x.name) for x in self.fields]

    def set(self, value):
        self.value = value
        self.run_rules()
        if self.errors:  # returns any errors
            return self.errors
        self.metadata.rules = []  # default
        self.set_fields(self.fields)
        logging.debug("TimeseriesCheck: data field is set as {}".format(self.data))
        return self.errors

    def run_check(self, new_check, metadata_names=[], other_data = None):
        """
        Returns errors only from that check
        :param other_data:
        :param new_check:
        :param metadata_names:
        :return:
        """
        self.metadata.rules = [rule.has_field(name) for name in metadata_names]
        errors = self.validate_field(self.metadata)  # automatically adds new errors to self.errors
        if errors:  # new errors from check
            return
        error = new_check.run(self.data.value, self.metadata, other_data)
        if not error.empty():  # Then fill in the rest of the info
            error.timeseries_code = self.metadata.id
            error.check_name = new_check.name
            error.company = self.company
            error.reference = self.reference
            error.api_call = self.api_call
            self.error(error)
        return

    def error(self, err: Error):
        logging.error(err)  # ERROR:root:error message
        self.errors.append(err)
        return

    def error_many(self, error_lst: list):
        if error_lst:
            self.errors += error_lst
        return

