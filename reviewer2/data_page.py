from flask import request, Response

from reviewer2 import args, RELATIVE_DIRECTORY_TO_DATA_FILES_LIST, FORM_SCHEMA, FORM_RESPONSES, \
    RELATIVE_DIRECTORY_TO_METADATA, FORM_RADIO_BUTTON_KEYBOARD_SHORTCUTS
from reviewer2.utils import load_jinja_template, get_data_page_url, CONTENT_HTML_FILE_TYPE, IMAGE_FILE_TYPE

DATA_PAGE_TEMPLATE = None


def data_page_handler():
    global DATA_PAGE_TEMPLATE
    if DATA_PAGE_TEMPLATE is None or args.dev_mode:
        DATA_PAGE_TEMPLATE = load_jinja_template("data_page")

    params = {}
    if request.values:
        params.update(request.values)

    if args.verbose:
        print(f"data_page_handler received {request.url}")

    if 'i' not in params:
        params.update(request.get_json(force=True, silent=True) or {})

    i = params.get("i")
    try:
        i = int(i)
    except (ValueError, TypeError):
        i = 1

    last = params.get("last", i)
    try:
        last = int(last)
    except (ValueError, TypeError):
        last = i

    if i < 1 or i > len(RELATIVE_DIRECTORY_TO_DATA_FILES_LIST):
        i = 1

    relative_dir, data_file_types_and_paths = RELATIVE_DIRECTORY_TO_DATA_FILES_LIST[i - 1]

    image_file_paths = []
    for data_file_type, data_file_path in data_file_types_and_paths:
        if data_file_type == IMAGE_FILE_TYPE:
            image_file_paths.append(data_file_path)

    metadata_json_dict = RELATIVE_DIRECTORY_TO_METADATA.get(relative_dir, {})

    content_html_strings = []
    for data_file_type, data_file_path in data_file_types_and_paths:
        if data_file_type != CONTENT_HTML_FILE_TYPE:
            continue
        with open(data_file_path, "rt") as f:
            content_string = f.read()
            content_html_strings.append((data_file_path, content_string))

    html = DATA_PAGE_TEMPLATE.render(
        i=i,
        last=last,
        relative_directory=relative_dir,
        image_file_paths=image_file_paths,
        metadata_json_dict=metadata_json_dict,
        content_html_strings=content_html_strings,
        get_data_page_url=get_data_page_url,
        form_schema=FORM_SCHEMA,
        form_radio_button_keyboard_shortcuts=FORM_RADIO_BUTTON_KEYBOARD_SHORTCUTS,
        form_responses=FORM_RESPONSES.get(relative_dir, {}),
    )

    return Response(html, mimetype='text/html')
