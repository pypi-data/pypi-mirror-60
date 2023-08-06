import os
import re
from tqdm import tqdm
from pathlib import Path
from pdfminer.high_level import extract_text


def get_file_names_from_dir(directory):
    files_list = []
    for dirname, dirlist, filelist in os.walk(Path(directory).expanduser().resolve()):
        for file_name in filelist:
            _file_path = Path(dirname) / file_name
            if _file_path.suffix == ".pdf":
                files_list.append(_file_path)
    return files_list


def list_files(paths):
    files_list = []
    for path in paths:
        path = Path(path).expanduser().resolve()
        if not path.exists():
            print(f"{path} does not exist?")
        elif path.is_dir():
            files_list.extend(get_file_names_from_dir(path))
        elif path.is_file():
            files_list.append(path)
        else:
            print(f"{path} is not a valid path?")
    return set(files_list)


def search_string_in_files(regex, paths):
    assert isinstance(paths, (list, tuple)), "`paths` should be a list"
    files_list = list_files(paths)
    print(f"Looking in {len(files_list)} file(s)")
    regex = re.compile(regex, re.IGNORECASE)
    print(f"looking for {regex}")
    mathced_file_list = []
    for _file in tqdm(files_list):
        content = extract_text(_file)[:200]
        match = re.match(regex, content)
        if match is not None:
            mathced_file_list.append(_file.name)
    print("Matched files are:", *["\t" + n for n in mathced_file_list], sep="\n")
