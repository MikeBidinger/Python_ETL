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
    del_data = E_Delimited(CONFIG["extract"]["delimited"]).parse()

    # - Parse positional data
    pos_data = E_Positional(CONFIG["extract"]["positional"]).parse(5)

    # - Parse Excel data
    excel_data = E_Excel(CONFIG["extract"]["excel"]).parse(100)

    # - Parse JSON data
    lookup = E_JSON(CONFIG["extract"]["json_lookup"]).parse()

    # Transform:

    # - Join data (left join)
    join = T_Join(CONFIG["transform"]["join_1"]).join(del_data, lookup)

    # Load:

    # - Write joined data as delimited
    file_path = L_Delimited(CONFIG["load"]["delimited"]).load(join.copy())
    print(file_path)

    # - Write joined data as positional
    file_path = L_Positional(CONFIG["load"]["positional"]).load(join.copy())
    print(file_path)

    # - Write joined data as Excel
    file_path = L_Excel(CONFIG["load"]["excel"]).load(join.copy())
    print(file_path)
