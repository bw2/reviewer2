import collections
from jinja2 import Template
import json
import os
import pandas as pd
import pkg_resources
from wcmatch import glob

IMAGE_FILE_TYPE = "image"
METADATA_JSON_FILE_TYPE = "metadata_json"
CONTENT_HTML_FILE_TYPE = "content_html"

METADATA_JSON_FILE_SUFFIX = "reviewer2_metadata.json"
CONTENT_HTML_FILE_SUFFIX = "reviewer2_content.html"


def get_relative_directory_to_data_files_list(
    top_level_dir,
    keywords_to_exclude,
    suffixes=("svg", "png", "jpeg", "jpg", "gif", "webp", CONTENT_HTML_FILE_SUFFIX, METADATA_JSON_FILE_SUFFIX),
    verbose=False):
    data_file_paths = []

    print(f"Looking for " + ", ".join(suffixes[:-1]) + f", and {suffixes[-1]} files in {top_level_dir}")
    glob_string = "|".join([os.path.join(top_level_dir, f"**/*{suffix}") for suffix in suffixes])
    matching_paths = glob.glob(glob_string, flags=glob.GLOBSTAR|glob.SPLIT)
    data_file_paths += matching_paths

    # group data files by their directory
    data_file_counter_by_suffix = collections.defaultdict(int)
    relative_directory_to_data_files = collections.defaultdict(list)
    excluded_keyword_to_matching_paths = collections.defaultdict(list)
    for data_file_path in data_file_paths:
        data_file_path = os.path.realpath(data_file_path)
        for suffix in suffixes:
            if data_file_path.endswith(suffix):
                data_file_suffix = suffix
                break
        else:
            raise Exception(f"Unexpected file suffix: {data_file_path}")
        data_file_counter_by_suffix[data_file_suffix] += 1
        relative_data_file_path = os.path.relpath(data_file_path, top_level_dir)
        excluded_keyword_matches = [k for k in keywords_to_exclude if k in relative_data_file_path] if keywords_to_exclude else []
        if excluded_keyword_matches:
            excluded_keyword_to_matching_paths[excluded_keyword_matches[0]].append(relative_data_file_path)
            if verbose:
                print(f"Skipping {data_file_suffix} file: {relative_data_file_path} - it contains excluded keyword: '{excluded_keyword_matches[0]}'")
            continue
        else:
            if verbose:
                print(f"{data_file_suffix} file: {relative_data_file_path}")

        key = os.path.dirname(relative_data_file_path)
        if not key or key == ".":
            key = relative_data_file_path

        if data_file_suffix == METADATA_JSON_FILE_SUFFIX:
            data_file_type = METADATA_JSON_FILE_TYPE
        elif data_file_suffix == CONTENT_HTML_FILE_SUFFIX:
            data_file_type = CONTENT_HTML_FILE_TYPE
        else:
            data_file_type = IMAGE_FILE_TYPE

        relative_directory_to_data_files[key].append((data_file_type, relative_data_file_path))

    data_file_counter_string = " and ".join([f"{c} {suffix} files" for suffix, c in data_file_counter_by_suffix.items()])
    print(f"Found {data_file_counter_string}" + (
        f" in {len(relative_directory_to_data_files)} sub-directories" if len(relative_directory_to_data_files) > 1 else ""
    ))

    for excluded_keyword, matching_paths in excluded_keyword_to_matching_paths.items():
        print(f"Skipped {len(matching_paths)} paths which contained excluded keyword: '{excluded_keyword}'")

    relative_directory_to_data_files_list = list(sorted(relative_directory_to_data_files.items()))

    return relative_directory_to_data_files_list


def get_relative_directory_to_metadata(top_level_dir, relative_directory_to_data_files_list, verbose=False):
    metadata_columns = collections.OrderedDict()
    relative_directory_to_metadata = {}
    # if it exists, parse the reviewer2_metadata.json file from each directory
    for relative_dir, data_files_list in relative_directory_to_data_files_list:
        for data_file_type, data_file_path in data_files_list:
            if data_file_type != METADATA_JSON_FILE_TYPE:
                continue

            metadata_json_path = os.path.join(top_level_dir, relative_dir, data_file_path)
            try:
                with open(metadata_json_path, "rt") as f:
                    metadata_json = json.load(f)
            except Exception as e:
                print(f"Unable to parse {metadata_json_path}: {e}")
                continue

            if not isinstance(metadata_json, dict):
                print(f"WARNING: {metadata_json_path} doesn't contain a dictionary. Skipping...")
                continue

            if verbose:
                print(f"Parsed {len(metadata_json)} metadata entries from {metadata_json_path}") # Keys: {', '.join(metadata_json.keys())}

            relative_directory_to_metadata[relative_dir] = metadata_json

            for key in metadata_json:
                metadata_columns[key] = None

    print(f"Found {len(relative_directory_to_metadata)} {METADATA_JSON_FILE_SUFFIX} files" + (
        f" with columns: {', '.join(metadata_columns)}" if metadata_columns else ""))

    return list(metadata_columns.keys()), relative_directory_to_metadata


def is_excel_table(path):
    return any(path.endswith(suffix) for suffix in ("xls", "xlsx"))


def parse_table(path):
    if not os.path.isfile(path):
        raise ValueError(f"{path} not found")

    try:
        if is_excel_table(path):
            df = pd.read_excel(path)
        else:
            df = pd.read_table(path)
    except Exception as e:
        raise ValueError(f"Unable to parse {path}: {e}")

        # validate table contents
    if 'Path' not in df.columns:
        raise ValueError(f"{path} must have a column named 'Path'")

    df.set_index('Path', inplace=True, drop=False)

    df = df.fillna('')
    print(f"Parsed {len(df)} rows from {path}")

    return df


def get_data_page_url(page_number, last):
    return f"/page?last={last}&i={page_number}"


def load_jinja_template(name):
    return Template(pkg_resources.resource_stream("reviewer2", f"templates/{name}.html").read().decode('UTF-8'))
