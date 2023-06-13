# ------------------------------------------------------------------------------
# Developer: Mike Bidinger
# Date:      2023-06-06
# Script:    Main of ETL-Process
# ------------------------------------------------------------------------------

from utils.json_functions import read_json
from utils.etl_extract import E_Delimited, E_Positional, E_Excel, E_XML, E_JSON
from utils.etl_transform import T_Join, T_Group
from utils.etl_load import L_Delimited, L_Positional, L_Excel, L_XML, L_JSON

CONFIG = read_json("config.json")

if __name__ == "__main__":

    # Extract:

    # - Parse delimited data
    data = E_Delimited(CONFIG["extract"]["delimited_1"]).parse()
    print(data)

    # - Parse JSON data
    lookup = E_JSON(CONFIG["extract"]["json_lookup"]).parse()
    print(lookup)

    # Transform:

    # - Join data
    join = T_Join(CONFIG["transform"]["join_1"]).join(data, lookup)
    print(join)

    # Load:

    # - Write joined data as delimited
    file_path = L_Delimited(CONFIG["load"]["delimited_1"]).load(join)
    print(file_path)
