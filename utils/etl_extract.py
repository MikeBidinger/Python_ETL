# ------------------------------------------------------------------------------
# Developer: Mike Bidinger
# Date:      2023-06-06
# Script:    Extraction of data
# ------------------------------------------------------------------------------

import xmltodict
import openpyxl
from .json_functions import read_json


def read_text_lines(file_path: str, nr_lines: int = 0, encoding: str = None):
    data = []
    with open(file_path, "r", encoding=encoding) as f:
        if nr_lines == 0:
            for x in f:
                data.append(x.replace("\n", ""))
        else:
            for i in range(0, nr_lines):
                data.append(f.readline())
    return data


def read_xml(file_path: str):
    data = ""
    with open(file_path, "r") as f:
        data = xmltodict.parse(f.read())
    return data


class E_Delimited:
    def __init__(self, config_data):
        self.file_path = config_data["file_path"]
        self.headers = config_data["headers"]
        self.delimiter = config_data["delimiter"]

    def parse(self):
        data = []
        # Get data from file
        rows = read_text_lines(self.file_path)
        # Add headers (optional)
        if self.headers != []:
            data.append(self.headers)
        # Parse positions for each row
        for row in rows:
            data.append(row.split(self.delimiter))
        # Return parsed data
        return data


class E_Positional:
    def __init__(self, config_data):
        self.file_path = config_data["file_path"]
        self.headers = config_data["headers"]
        self.positions = config_data["positions"]

    def parse(self):
        data = []
        # Get data from file
        rows = read_text_lines(self.file_path)
        # Add headers (optional)
        if self.headers != []:
            data.append(self.headers)
        # Parse positions for each row
        for row in rows:
            row_data = []
            for idx, position in enumerate(self.positions):
                if idx + 1 < len(self.positions):
                    row_data.append(row[position : self.positions[idx + 1]])
                else:
                    row_data.append(row[position:])
            data.append(row_data)
        # Return parsed data
        return data


class E_Excel:
    def __init__(self, config_data):
        self.file_path = config_data["file_path"]
        self.headers = config_data["headers"]

    def parse(self):
        data = []
        # Get data from workbook
        wb = openpyxl.load_workbook(self.file_path)
        # Get data from sheet
        sh = wb.active
        # Add headers (optional)
        if self.headers != []:
            data.append(self.headers)
        # Parse data
        for row in range(0, sh.max_row):
            row_data = []
            for col in sh.iter_cols(1, sh.max_column):
                if col[row].value is None:
                    row_data.append("")
                else:
                    row_data.append(col[row].value)
            data.append(row_data)
        # Return parsed data
        return data


class E_XML:
    def __init__(self, config_data):
        self.file_path = config_data["file_path"]
        self.xpath = config_data["xpath"]

    def parse(self):
        data = []
        # Get data from file
        xml = read_xml(self.file_path)
        # Get data according to XPath
        loop = self.xpath.split("/")[1:]
        elements = []
        for idx, element in enumerate(loop):
            if element == "":
                # Collect all given elements of descendant
                self._loop_children(xml, loop[idx + 1], elements)
            elif element in xml:
                xml = xml[element]
        if elements != []:
            # Set element data
            xml = []
            for x in elements:
                for y in x:
                    xml.append(y)
        # Collect all headers
        headers = {}
        row_headers = []
        for row in xml:
            for header in row:
                if header not in headers:
                    headers[header] = len(headers)
                    row_headers.append(header)
        # Parse data
        data.append(row_headers)
        for row in xml:
            row_data = ["" for x in headers]
            for header in row:
                if row[header] == None:
                    row_data[headers[header]] = ""
                else:
                    row_data[headers[header]] = row[header]
            data.append(row_data)
        # Return parsed data
        return data

    def _loop_children(self, xml, element, elements):
        for x in xml:
            if x == element:
                elements.append(xml[x])
            elif type(xml[x]) is not str and len(xml[x]) > 0:
                self._loop_children(xml[x], element, elements)


class E_JSON:
    def __init__(self, config_data):
        self.file_path = config_data["file_path"]
        self.xpath = config_data["xpath"]

    def parse(self):
        data = []
        # Get data from file
        json = read_json(self.file_path)
        # Get data according to XPath
        loop = self.xpath.split("/")[1:]
        elements = []
        for idx, element in enumerate(loop):
            if element == "":
                # Collect all given elements of descendant
                self._loop_children(json, loop[idx + 1], elements)
            elif element in json:
                json = json[element]
        if elements != []:
            # Set element data
            json = []
            for x in elements:
                for y in x:
                    json.append(y)
        # Collect all headers
        headers = {}
        row_headers = []
        for row in json:
            for header in row:
                if header not in headers:
                    headers[header] = len(headers)
                    row_headers.append(header)
        # Parse data
        data.append(row_headers)
        for row in json:
            row_data = ["" for x in headers]
            for header in row:
                if row[header] == None:
                    row_data[headers[header]] = ""
                else:
                    row_data[headers[header]] = row[header]
            data.append(row_data)
        # Return parsed data
        return data

    def _loop_children(self, json, element, elements):
        for x in json:
            if x == element:
                elements.append(json[x])
            elif type(json[x]) is not str and len(json[x]) > 0:
                self._loop_children(json[x], element, elements)


if __name__ == "__main__":

    CONFIG = read_json("config.json")

    # Extract data (parse data from files):

    # - Delimited:
    #   - Including headers
    data = E_Delimited(CONFIG["extract"]["delimited_1"]).parse()
    print(data)
    #   - Excluding headers
    data = E_Delimited(CONFIG["extract"]["delimited_2"]).parse()
    print(data)

    # - Positional:
    #   - Including headers
    data = E_Positional(CONFIG["extract"]["positional_1"]).parse()
    print(data)
    #   - Excluding headers
    data = E_Positional(CONFIG["extract"]["positional_2"]).parse()
    print(data)

    # - Excel:
    #   - Including headers
    data = E_Excel(CONFIG["extract"]["excel_1"]).parse()
    print(data)
    #   - Excluding headers
    data = E_Excel(CONFIG["extract"]["excel_2"]).parse()
    print(data)

    # - XML
    data = E_XML(CONFIG["extract"]["xml_1"]).parse()
    print(data)
    data = E_XML(CONFIG["extract"]["xml_2"]).parse()
    print(data)
    data = E_XML(CONFIG["extract"]["xml_3"]).parse()
    print(data)

    # - JSON
    data = E_JSON(CONFIG["extract"]["json_1"]).parse()
    print(data)
    data = E_JSON(CONFIG["extract"]["json_2"]).parse()
    print(data)
    data = E_JSON(CONFIG["extract"]["json_3"]).parse()
    print(data)
