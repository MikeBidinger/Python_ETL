# ------------------------------------------------------------------------------
# Developer: Mike Bidinger
# Date:      2023-06-06
# Script:    Loading of data
# ------------------------------------------------------------------------------

import openpyxl
from .json_functions import read_json, write_json
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString


def write_result_list(data: list, file_path: str, append=False):
    if append:
        mode = "a"
    else:
        mode = "w"
    with open(file_path, mode) as f:
        for row in data:
            f.write(row + "\n")
    return file_path


def write_xml(data: dict, file_path: str, attr_type=False, append=False):
    if append:
        mode = "a"
    else:
        mode = "w"
    my_item_func = lambda x: "row"
    xml = dicttoxml(data, attr_type=attr_type, item_func=my_item_func)
    dom = parseString(xml)
    with open(file_path, mode) as f:
        f.write(dom.toprettyxml())
    return file_path


class L_Delimited:
    def __init__(self, config_data):
        self.file_path = config_data["file_path"]
        self.delimiter = config_data["delimiter"]
        self.append = config_data["append"]

    def load(self, data):
        # Set data delimited
        for idx, row in enumerate(data):
            data[idx] = self.delimiter.join(row)
        # Load data to delimited file
        return write_result_list(data, self.file_path, self.append)


class L_Positional:
    def __init__(self, config_data):
        self.file_path = config_data["file_path"]
        self.positions = config_data["positions"]
        self.headers = config_data["headers"]
        self.append = config_data["append"]
        self.lengths = self._set_lengths()

    def _set_lengths(self):
        lengths = []
        for i in range(len(self.positions) - 1):
            lengths.append(self.positions[i + 1] - self.positions[i])
        lengths.append(-1)
        return lengths

    def load(self, data):
        # Set data positional
        if not self.headers:
            data = data[1:]
        for idx, row in enumerate(data):
            row_data = ""
            for idy, val in enumerate(row):
                row_data += val.ljust(self.lengths[idy], " ")
            data[idx] = row_data
        # Load data to delimited file
        return write_result_list(data, self.file_path, self.append)


class L_Excel:
    def __init__(self, config_data):
        self.file_path = config_data["file_path"]

    def load(self, data):
        # Create workbook
        wb = openpyxl.Workbook()
        # Load data to sheet
        sh = wb.active
        for idx, row in enumerate(data):
            for idy, val in enumerate(row):
                sh.cell(idx + 1, idy + 1).value = val
        # Save workbook
        wb.save(self.file_path)
        return self.file_path


class L_XML:
    def __init__(self, config_data):
        self.file_path = config_data["file_path"]
        self.attr_type = config_data["attr_type"]
        self.append = config_data["append"]

    def load(self, data):
        # Set data to dictionary
        xml = []
        for row in data[1:]:
            xml.append({})
            for idy, val in enumerate(row):
                xml[-1][data[0][idy]] = val
        # Load dictionary to xml file
        return write_xml(xml, self.file_path, self.attr_type, self.append)


class L_JSON:
    def __init__(self, config_data):
        self.file_path = config_data["file_path"]

    def load(self, data):
        # Set data to dictionary
        json = []
        for row in data[1:]:
            json.append({})
            for idy, val in enumerate(row):
                json[-1][data[0][idy]] = val
        # Load dictionary to json file
        return write_json(self.file_path, json)


if __name__ == "__main__":

    CONFIG = read_json("config.json")

    data = [
        ["KOGR", "PPG", "Part_Nr", "DH"],
        ["5678", "002", "1234567", "WX"],
        ["1234", "001", "5A12345", "OD"],
    ]

    # Load data:

    # - Delimited
    # file_path = L_Delimited(CONFIG["load"]["delimited_1"]).load(data)
    # print(file_path)

    # - Positional
    # file_path = L_Positional(CONFIG["load"]["positional_1"]).load(data)
    # print(file_path)
    # file_path = L_Positional(CONFIG["load"]["positional_2"]).load(data)
    # print(file_path)

    # - Excel
    # file_path = L_Excel(CONFIG["load"]["excel_1"]).load(data)
    # print(file_path)

    # - XML
    # file_path = L_XML(CONFIG["load"]["xml_1"]).load(data)
    # print(file_path)

    # - JSON
    file_path = L_JSON(CONFIG["load"]["json_1"]).load(data)
    print(file_path)
