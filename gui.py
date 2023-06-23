# ------------------------------------------------------------------------------
# Developer: Mike Bidinger
# Date:      2023-06-23
# Script:    GUI for file conversion (using ETL-Process)
# ------------------------------------------------------------------------------

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from pathlib import Path
import re
from utils.json_functions import read_json, write_json
from utils.etl_extract import E_Delimited, E_Positional, E_Excel, E_XML, E_JSON
from utils.etl_load import L_Delimited, L_Positional, L_Excel, L_XML, L_JSON

RES = "900x900"

BG = "#333333"
GRAY = "#262626"
GRAY_D = "#1A1A1A"
WHITE = "#DDDDDD"
BLACK = "#000000"
GREEN = "#00A940"

TITLE = ("Arial", 18, "bold")
SUBTITLE = ("Arial", 16, "bold")

INIT_DIR = Path(__file__).parent
FILE_PAT = "[a-zA-Z0-9][.][a-zA-Z]{2}"
SEP = ";"
PRE_LINES = 15


def file_selection_dialog(title, file_type="", initial_dir=INIT_DIR):
    file_types = [("All Files", "*.*")]
    if file_type == "delimited":
        file_types.insert(0, ("Delimited Files", "*.csv *.txt"))
    elif file_type == "positional":
        file_types.insert(0, ("Positional Files", "*.txt"))
    elif file_type == "excel":
        file_types.insert(0, ("Excel Files", "*.xlsx"))
    elif file_type == "xml":
        file_types.insert(0, ("XML Files", "*.xml"))
    elif file_type == "json":
        file_types.insert(0, ("JSON Files", "*.json"))
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        filetypes=file_types, initialdir=initial_dir, title=title
    )
    return file_path


def folder_selection_dialog(title, initial_dir=INIT_DIR):
    root = tk.Tk()
    root.withdraw()
    dir_path = filedialog.askdirectory(initialdir=initial_dir, title=title)
    return dir_path


def file_save_dialog(title, file_type, initial_dir=INIT_DIR):
    if file_type == "delimited":
        file_types = [("Delimited Files", "*.csv *.txt")]
    elif file_type == "positional":
        file_types = [("Positional Files", "*.txt")]
    elif file_type == "excel":
        file_types = [("Excel Files", "*.xlsx")]
    elif file_type == "xml":
        file_types = [("XML Files", "*.xml")]
    elif file_type == "json":
        file_types = [("JSON Files", "*.json")]
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(
        filetypes=file_types, initialdir=initial_dir, title=title
    )
    return file_path


def read_text_line(file_path):
    data = ""
    with open(file_path, "r") as f:
        data = f.readline()
    data = data.rsplit("\n", 1)[0]
    return data


class ETL_GUI:
    def __init__(self):
        # Root window
        self.root = tk.Tk()
        self.root.title("File Conversion GUI")
        self.root.geometry(RES)
        self.root.config(bg=BG)

        # Menubar:
        self.menubar = tk.Menu(self.root)
        # - File Menu
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open Configuration", command=self.open_config)
        self.filemenu.add_command(label="Save Configuration", command=self.save_config)
        # Add menu's to menubar
        self.menubar.add_cascade(menu=self.filemenu, label="File")
        # Add menubar to root window
        self.root.config(menu=self.menubar)

        # Title Label
        self.title_label = tk.Label(
            self.root, text="File Conversion:", font=TITLE, bg=BG, fg=GREEN
        )
        self.title_label.pack(padx=10, pady=5)

        # Extraction
        self._init_extract(bg=GRAY, fg=WHITE, title_color=GREEN)
        self.e_frame.pack(fill="x")

        # Load
        self._init_load(bg=GRAY_D, fg=WHITE, title_color=GREEN)
        self.l_frame.pack(fill="x")

        # Button Frame:
        self.btn_frame = tk.Frame(self.root, pady=10, bg=BG)
        # - Preview
        tk.Button(
            self.btn_frame,
            text="Preview Extraction",
            command=self.preview,
            bg=BLACK,
            fg=WHITE,
            activebackground=GREEN,
            activeforeground=WHITE,
        ).grid(row=0, column=0, padx=5)
        # - Start
        self.start_btn = tk.Button(
            self.btn_frame,
            text="Start Conversion",
            command=self.start_etl,
            bg=BLACK,
            fg=WHITE,
            activebackground=GREEN,
            activeforeground=WHITE,
        )
        # Pack
        self.btn_frame.pack()

        # Preview Frame
        self.pre_frame = tk.Frame(self.root, pady=10, padx=10, bg=GRAY)
        self.pre_text = tk.Text(
            self.pre_frame, wrap="none", bg=BLACK, fg=WHITE, insertbackground=GREEN
        )
        self.pre_text.pack(fill="x")

        # Close-handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.root.mainloop()

    def _init_extract(self, bg, fg, title_color):
        self.e_frame = tk.Frame(self.root, pady=5, bg=bg)
        # Label
        tk.Label(
            self.e_frame, text="Input", font=SUBTITLE, bg=bg, fg=title_color
        ).pack()
        # File Type Selection
        (
            self.e_filetype,
            self.var_e_type,
            self.e_del_frame,
            self.var_e_del,
            self.e_pos_frame,
            self.var_e_pos,
            self.xpath_frame,
            self.var_xpath,
        ) = self._init_filetype(self.e_frame, self.browse_e_positions, bg, fg)
        self.e_filetype.pack(anchor=tk.W)
        # File Path Entry
        self.e_filepath, self.var_e_path = self._init_filepath(
            self.e_frame, self.browse_extraction, bg, fg
        )
        self.e_filepath.pack(fill="x")
        # Header Entry
        (
            self.e_header,
            self.e_header_menu,
            self.var_e_header_state,
            self.var_e_headers,
        ) = self._init_header(
            self.e_frame, self.browse_e_headers, "File contains headers", bg, fg
        )
        self.e_header.pack(fill="x")
        # Delimiter Entry
        self.e_del_frame.pack(fill="x")

    def _init_load(self, bg, fg, title_color):
        self.l_frame = tk.Frame(self.root, pady=5, bg=bg)
        # Label
        tk.Label(
            self.l_frame, text="Output", font=SUBTITLE, bg=bg, fg=title_color
        ).pack()
        # File Type Selection
        (
            self.l_filetype,
            self.var_l_type,
            self.l_del_frame,
            self.var_l_del,
            self.l_pos_frame,
            self.var_l_pos,
            _,
            _,
        ) = self._init_filetype(self.l_frame, self.browse_l_positions, bg, fg)
        self.l_filetype.pack(anchor=tk.W)
        # File Path Entry
        self.l_filepath, self.var_l_path = self._init_filepath(
            self.l_frame, self.browse_load, bg, fg
        )
        self.l_filepath.pack(fill="x")
        # Header Entry
        (
            self.l_header,
            self.l_header_menu,
            self.var_l_header_state,
            self.var_l_headers,
        ) = self._init_header(
            self.l_frame, self.browse_l_headers, "Output all headers", bg, fg
        )
        self.l_header.pack(fill="x")
        # Delimiter Entry
        self.l_del_frame.pack(fill="x")

    def _init_filetype(self, parent, command, bg, fg):
        filetype = tk.Frame(parent, padx=10, pady=5, bg=bg)
        filetype.columnconfigure(0, weight=0)
        filetype.columnconfigure(1, weight=1)
        filetype.columnconfigure(2, weight=0)
        tk.Label(filetype, text="Select file type to extract:", bg=bg, fg=fg).grid(
            row=0, column=0, sticky=tk.W
        )
        e_rb_frame = tk.Frame(filetype, bg=bg)
        var_type = tk.StringVar(parent, "delimited")
        var_type.trace("w", lambda a, b, c: self.type_check())
        e_types = {
            "Delimited": "delimited",
            "Positional": "positional",
            "Excel": "excel",
            "XML": "xml",
            "JSON": "json",
        }
        for (text, value) in e_types.items():
            tk.Radiobutton(
                e_rb_frame,
                text=text,
                variable=var_type,
                value=value,
                bg=bg,
                fg=fg,
                activebackground=bg,
                activeforeground=GREEN,
                selectcolor=BLACK,
            ).pack(anchor=tk.W)
        e_rb_frame.grid(row=1, column=0)
        # Delimited Entry (file type selection depended)
        del_frame = tk.Frame(parent, padx=10, pady=5, bg=bg)
        del_frame.columnconfigure(0, weight=0)
        del_frame.columnconfigure(1, weight=1)
        del_frame.columnconfigure(2, weight=0)
        tk.Label(del_frame, text="Delimiter:", bg=bg, fg=fg).grid(
            row=0, column=0, sticky=tk.W
        )
        var_del = tk.StringVar(parent)
        var_del.trace("w", lambda a, b, c: self.start_check())
        tk.Entry(
            del_frame, textvariable=var_del, bg=BLACK, fg=WHITE, insertbackground=GREEN
        ).grid(row=0, column=1, sticky=tk.W + tk.E)
        # Positional Entry (file type selection depended)
        pos_frame = tk.Frame(parent, padx=10, pady=5, bg=bg)
        pos_frame.columnconfigure(0, weight=0)
        pos_frame.columnconfigure(1, weight=1)
        pos_frame.columnconfigure(2, weight=0)
        tk.Label(pos_frame, text="Positions:", bg=bg, fg=fg).grid(
            row=0, column=0, sticky=tk.W
        )
        var_pos = tk.StringVar(parent)
        var_pos.trace("w", lambda a, b, c: self.position_check())
        tk.Entry(
            pos_frame, textvariable=var_pos, bg=BLACK, fg=WHITE, insertbackground=GREEN
        ).grid(row=0, column=1, sticky=tk.W + tk.E)
        tk.Button(
            pos_frame,
            text="Browse",
            command=command,
            bg=BLACK,
            fg=WHITE,
            activebackground=GREEN,
            activeforeground=WHITE,
        ).grid(row=0, column=2, padx=10, sticky=tk.E)
        # Xpath Entry (file type selection depended)
        xpath_frame = tk.Frame(parent, padx=10, pady=5, bg=bg)
        xpath_frame.columnconfigure(0, weight=0)
        xpath_frame.columnconfigure(1, weight=1)
        xpath_frame.columnconfigure(2, weight=0)
        tk.Label(xpath_frame, text="Xpath:", bg=bg, fg=fg).grid(
            row=0, column=0, sticky=tk.W
        )
        var_xpath = tk.StringVar(parent)
        var_xpath.trace("w", lambda a, b, c: self.start_check())
        tk.Entry(
            xpath_frame,
            textvariable=var_xpath,
            bg=BLACK,
            fg=WHITE,
            insertbackground=GREEN,
        ).grid(row=0, column=1, sticky=tk.W + tk.E)
        return (
            filetype,
            var_type,
            del_frame,
            var_del,
            pos_frame,
            var_pos,
            xpath_frame,
            var_xpath,
        )

    def _init_filepath(self, parent, command, bg, fg):
        filepath = tk.Frame(parent, padx=10, pady=5, bg=bg)
        filepath.columnconfigure(0, weight=0)
        filepath.columnconfigure(1, weight=1)
        filepath.columnconfigure(2, weight=0)
        tk.Label(filepath, text="Select file path to extract:", bg=bg, fg=fg).grid(
            row=0, column=0, sticky=tk.W
        )
        var_path = tk.StringVar(parent)
        var_path.trace("w", lambda a, b, c: self.start_check())
        tk.Entry(
            filepath, textvariable=var_path, bg=BLACK, fg=WHITE, insertbackground=GREEN
        ).grid(row=0, column=1, sticky=tk.W + tk.E)
        tk.Button(
            filepath,
            text="Browse",
            command=command,
            bg=BLACK,
            fg=WHITE,
            activebackground=GREEN,
            activeforeground=WHITE,
        ).grid(row=0, column=2, padx=10, sticky=tk.E)
        return filepath, var_path

    def _init_header(self, parent, command, text, bg, fg):
        header_frame = tk.Frame(parent, padx=10, pady=5, bg=bg)
        header_frame.columnconfigure(0, weight=0)
        header_frame.columnconfigure(1, weight=1)
        header_frame.columnconfigure(2, weight=0)
        var_header_state = tk.IntVar(value=1)
        var_header_state.trace("w", lambda a, b, c: self.header_menu())
        tk.Checkbutton(
            header_frame,
            text=text,
            variable=var_header_state,
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground=GREEN,
            selectcolor=BLACK,
        ).grid(row=0, column=0, sticky=tk.W)
        # Header Entry (header selection depended)
        header_menu_frame = tk.Frame(parent, padx=10, pady=5, bg=bg)
        header_menu_frame.columnconfigure(0, weight=0)
        header_menu_frame.columnconfigure(1, weight=1)
        header_menu_frame.columnconfigure(2, weight=0)
        tk.Label(header_menu_frame, text="Select headers:", bg=bg, fg=fg).grid(
            row=0, column=0, sticky=tk.W
        )
        var_header = tk.StringVar(parent)
        var_header.trace("w", lambda a, b, c: self.start_check())
        tk.Entry(
            header_menu_frame,
            textvariable=var_header,
            bg=BLACK,
            fg=WHITE,
            insertbackground=GREEN,
        ).grid(row=0, column=1, sticky=tk.W + tk.E)
        tk.Button(
            header_menu_frame,
            text="Browse",
            command=command,
            bg=BLACK,
            fg=WHITE,
            activebackground=GREEN,
            activeforeground=WHITE,
        ).grid(row=0, column=2, padx=10, sticky=tk.E)
        return header_frame, header_menu_frame, var_header_state, var_header

    def browse_extraction(self):
        file_path = file_selection_dialog(
            "Select extraction file", self.var_e_type.get()
        )
        if file_path != "":
            self.var_e_path.set(file_path)
        self.start_check()

    def browse_load(self):
        folder_path = folder_selection_dialog("Select load folder")
        if folder_path != "":
            self.var_l_path.set(folder_path)

    def browse_e_headers(self):
        self.browse_headers(self.var_e_headers)

    def browse_l_headers(self):
        self.browse_headers(self.var_l_headers)

    def browse_headers(self, var_headers):
        file_path = file_selection_dialog("Select header file", "delimited")
        if file_path != "":
            var_headers.set(read_text_line(file_path))

    def browse_e_positions(self):
        self.browse_positions(self.var_e_pos)

    def browse_l_positions(self):
        self.browse_positions(self.var_l_pos)

    def browse_positions(self, var_pos):
        file_path = file_selection_dialog("Select positions file", "delimited")
        if file_path != "":
            var_pos.set(read_text_line(file_path))
            self.position_check()
            self.start_check()

    def position_check(self):
        loop = [self.var_e_pos, self.var_l_pos]
        for var_pos in loop:
            val = var_pos.get()
            if val != "":
                if not val[-1].isdecimal():
                    if val[-1] != ";":
                        var_pos.set(val[:-1])
                    elif val[-1] == ";" and len(val) > 2:
                        if val[-2] == ";":
                            var_pos.set(val[:-1])

    def type_check(self):
        loop = [
            (
                self.e_del_frame,
                self.e_pos_frame,
                self.xpath_frame,
                self.var_e_type.get(),
                self.e_header,
                self.e_header_menu,
                self.var_e_header_state.get(),
            ),
            (
                self.l_del_frame,
                self.l_pos_frame,
                None,
                self.var_l_type.get(),
                None,
                None,
                None,
            ),
        ]
        for (
            del_frame,
            pos_frame,
            xpath_frame,
            var_type,
            header_frame,
            header_menu_frame,
            var_header_state,
        ) in loop:
            del_frame.pack_forget()
            pos_frame.pack_forget()
            if xpath_frame is not None:
                xpath_frame.pack_forget()
                header_frame.pack(fill="x")
                if not var_header_state:
                    header_menu_frame.pack(fill="x")
            if var_type == "delimited":
                del_frame.pack(fill="x")
            elif var_type == "positional":
                pos_frame.pack(fill="x")
            elif var_type == "xml" or var_type == "json":
                if xpath_frame is not None:
                    header_frame.pack_forget()
                    header_menu_frame.pack_forget()
                    xpath_frame.pack(fill="x")
        self.start_check()

    def header_menu(self):
        loop = [
            (self.var_e_header_state, self.e_header_menu),
            (self.var_l_header_state, self.l_header_menu),
        ]
        for state, menu in loop:
            if state.get():
                menu.pack_forget()
            else:
                menu.pack(fill="x")
        self.type_check()
        self.start_check()

    def start_etl(self):
        print("Starting...")
        # Get configuration settings
        config = self.get_config()
        # Extract data
        data = self.extract_data(config)
        # Load data
        print("Loaded:", self.load_data(config, data))
        print("...Done!")
        messagebox.showinfo("Conversion completed", "The conversion is completed!")

    def start_check(self):
        self.start_btn.grid_forget()
        e_path = self.var_e_path.get()
        l_path = self.var_l_path.get()
        if self.file_check(e_path) and self.folder_check(l_path):
            e_type = self.var_e_type.get()
            l_type = self.var_l_type.get()
            if (
                (
                    e_type == "delimited"
                    and ((e_path.endswith(".csv")) or (e_path.endswith(".txt")))
                )
                or (e_type == "positional" and e_path.endswith(".txt"))
                or (e_type == "excel" and e_path.endswith(".xlsx"))
                or (e_type == "xml" and e_path.endswith(".xml"))
                or (e_type == "json" and e_path.endswith(".json"))
            ) and (
                (
                    l_type == "delimited"
                    and ((l_path.endswith(".csv")) or (l_path.endswith(".txt")))
                )
                or (l_type == "positional" and l_path.endswith(".txt"))
                or (l_type == "excel" and l_path.endswith(".xlsx"))
                or (l_type == "xml" and l_path.endswith(".xml"))
                or (l_type == "json" and l_path.endswith(".json"))
            ):
                if (
                    self.var_e_header_state.get() or self.var_e_headers.get() != ""
                ) and (self.var_l_header_state.get() or self.var_l_headers.get() != ""):
                    self.start_btn.grid(row=0, column=1, padx=5)

    def file_check(self, var_path):
        file_path = var_path
        if file_path == "":
            return False
        else:
            return Path(file_path).is_file()

    def folder_check(self, var_path):
        file_path = var_path
        if file_path == "":
            return False
        else:
            file = Path(file_path)
            return file.parent.is_dir() and re.search(FILE_PAT, file.name)

    def get_config(self, file_path="gui_config.json"):
        # Get selected configuration
        config = {}
        loop = [
            (
                "extract",
                self.var_e_type.get(),
                self.var_e_path.get(),
                self.var_e_header_state.get(),
                self.var_e_headers.get(),
                self.var_e_del.get(),
                self.var_e_pos.get(),
                self.var_xpath.get(),
            ),
            (
                "load",
                self.var_l_type.get(),
                self.var_l_path.get(),
                self.var_l_header_state.get(),
                self.var_l_headers.get(),
                self.var_l_del.get(),
                self.var_l_pos.get(),
                None,
            ),
        ]
        for (
            action,
            var_type,
            var_path,
            var_header_state,
            var_headers,
            var_del,
            var_pos,
            var_xpath,
        ) in loop:
            config[action] = {}
            config[action][var_type] = {}
            config[action][var_type]["file_path"] = var_path
            config[action][var_type]["header_state"] = var_header_state
            if var_header_state:
                config[action][var_type]["headers"] = []
            else:
                config[action][var_type]["headers"] = var_headers.split(SEP)
            config[action][var_type]["delimiter"] = var_del.replace("\\t", "\t")
            config[action][var_type]["positions"] = []
            if var_type == "positional":
                positions = var_pos.split(SEP)
                for pos in positions:
                    if pos.isdecimal():
                        config[action][var_type]["positions"].append(int(pos))
            if var_xpath is not None:
                config[action][var_type]["xpath"] = var_xpath
        # Set configuration
        write_json(file_path, config)
        return config

    def open_config(self):
        file_path = file_selection_dialog("Select configuration file", "json")
        if file_path != "":
            config = read_json(file_path)
            loop = [
                (
                    "extract",
                    self.var_e_type,
                    self.var_e_path,
                    self.var_e_header_state,
                    self.var_e_headers,
                    self.var_e_del,
                    self.var_e_pos,
                    self.var_xpath,
                ),
                (
                    "load",
                    self.var_l_type,
                    self.var_l_path,
                    self.var_l_header_state,
                    self.var_l_headers,
                    self.var_l_del,
                    self.var_l_pos,
                    None,
                ),
            ]
            for (
                action,
                var_type,
                var_path,
                var_header_state,
                var_headers,
                var_del,
                var_pos,
                var_xpath,
            ) in loop:
                for key in config[action]:
                    file_type = key
                    break
                var_type.set(file_type)
                var_path.set(config[action][file_type]["file_path"])
                var_header_state.set(config[action][file_type]["header_state"])
                var_headers.set(SEP.join(config[action][file_type]["headers"]))
                var_del.set(config[action][file_type]["delimiter"].replace("\t", "\\t"))
                positions = []
                for pos in config[action][file_type]["positions"]:
                    positions.append(str(pos))
                var_pos.set(SEP.join(positions))
                if var_xpath is not None:
                    var_xpath.set(config[action][file_type]["xpath"])

    def save_config(self):
        file_path = file_save_dialog("Save configuration", "json")
        if file_path != "":
            if file_path.endswith(".json"):
                self.get_config(file_path)
            else:
                self.get_config(file_path + ".json")

    def extract_data(self, config, nr_lines=0):
        for type in config["extract"]:
            if type == "delimited":
                data = E_Delimited(config["extract"][type]).parse(nr_lines)
            elif type == "positional":
                data = E_Positional(config["extract"][type]).parse(nr_lines)
            elif type == "excel":
                data = E_Excel(config["extract"][type]).parse(nr_lines)
            elif type == "xml":
                data = E_XML(config["extract"][type]).parse(nr_lines)
            elif type == "json":
                data = E_JSON(config["extract"][type]).parse(nr_lines)
        return data

    def load_data(self, config, data):
        for type in config["load"]:
            if type == "delimited":
                file_path = L_Delimited(config["load"][type]).load(data)
            elif type == "positional":
                file_path = L_Positional(config["load"][type]).load(data)
            elif type == "excel":
                file_path = L_Excel(config["load"][type]).load(data)
            elif type == "xml":
                file_path = L_XML(config["load"][type]).load(data)
            elif type == "json":
                file_path = L_JSON(config["load"][type]).load(data)
        return file_path

    def preview(self):
        if self.file_check(self.var_e_path.get()):
            if self.var_e_header_state.get() or self.var_e_headers.get() != "":
                e_type = self.var_e_type.get()
                if (
                    (e_type == "delimited" and self.var_e_del.get() != "")
                    or (e_type == "positional")
                    or (e_type == "excel")
                    or (e_type == "xml")
                    or (e_type == "json")
                ):
                    # Get configuration settings
                    config = self.get_config()
                    # Extract preview data
                    if self.var_e_header_state.get():
                        preview_lines = PRE_LINES + 1
                    else:
                        preview_lines = PRE_LINES
                    data = self.extract_data(config, preview_lines)
                    # Get column dimensions of preview data
                    columns = self.preview_column_dimensions(data)
                    # Set preview data
                    text = self.preview_header(data, columns)
                    text += self.preview_data(data, columns)
                    self.pre_text.delete("1.0", tk.END)
                    self.pre_text.insert("1.0", text)
                    self.pre_frame.pack(fill="x")
                    return
        self.pre_frame.pack_forget()

    def preview_column_dimensions(self, data):
        columns = {}
        for row in data:
            for col, val in enumerate(row):
                if col in columns:
                    if columns[col] < len(val):
                        columns[col] = len(val)
                else:
                    columns[col] = len(val)
        return columns

    def preview_header(self, data, columns):
        text = ""
        header_separator = ""
        for col, header in enumerate(data[0]):
            text += "|" + header.ljust(columns[col])
            header_separator += "+".ljust(columns[col] + 1, "-")
        text = text + "|\n"
        text += header_separator + "+\n"
        data.pop(0)
        return text

    def preview_data(self, data, columns):
        text = ""
        for row in data:
            for col, val in enumerate(row):
                text += "|" + val.ljust(columns[col])
            text = text + "|\n"
        return text

    def on_closing(self):
        if messagebox.askyesno("Quit?", "Do you really want to quit?"):
            self.root.destroy()
            quit()


if __name__ == "__main__":

    gui = ETL_GUI()
