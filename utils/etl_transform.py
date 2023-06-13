# ------------------------------------------------------------------------------
# Developer: Mike Bidinger
# Date:      2023-06-07
# Script:    Transformation of data
# ------------------------------------------------------------------------------

from .json_functions import read_json


class T_Join:
    def __init__(self, config_data):
        self.key = config_data["key"]

    def join(self, table, lookup):
        data = []
        # Get header location of key in table
        for idx, header in enumerate(table[0]):
            if header == self.key:
                key_t = idx
                break
        # Get header location of key in lookup
        for idx, header in enumerate(lookup[0]):
            if header == self.key:
                key_l = idx
                break
        # Set lookup data
        join = {}
        for row in lookup:
            join[row[key_l]] = row
            join[row[key_l]].pop(key_l)
        # Join data
        for row in table:
            if row[key_t] in join:
                data.append(row + join[row[key_t]])
            else:
                data.append(row + ["" for x in join[self.key]])
        # Return joined data
        return data


class T_Group:
    def __init__(self, config_data):
        self.key = config_data["key"]
        self.group_header = config_data["group"]
        self.function = config_data["function"]

    def group(self, table):
        data = []
        # Get group header location in table
        for idx, header in enumerate(table[0]):
            if header == self.group_header:
                key_h = idx
                break
        # Group (function dependent)
        group = {}
        if self.function == "Sum":
            pass
        # Return grouped data
        return data


if __name__ == "__main__":

    CONFIG = read_json("config.json")

    data = [
        ["KOGR", "PPG", "Part_Nr", "Qty", "DH"],
        ["5678", "002", "1234567", "2", "WX"],
        ["1234", "001", "5A12345", "1", "OD"],
        ["1234", "001", "5A12345", "3", ""],
    ]

    lookup = [
        ["Part_Nr", "Description"],
        # ["1234567", "Part A"],
        ["7890123", "Part B"],
        ["5A12345", "Part C"],
    ]

    # Transform data:

    # - Join
    data = T_Join(CONFIG["transform"]["join_1"]).join(data, lookup)
    print(data)

    # - Group
    data = T_Group(CONFIG["transform"]["group_1"]).group(data)
