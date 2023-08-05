import json

import pandas as pd
from amazon.category.actions.parsers import get_categories


def _get_feed_path(category="", feed_path=""):
    """
    Get file path of feed template file for a given category
    """
    if bool(category) == bool(feed_path):
        raise AttributeError("Нужно задать либо категорию, либо путь к файлу")
    if category:
        return get_categories()[category]["feed_path"]
    return feed_path


def get_valid_fields_values(*, category="", feed_path="", to_json=False):
    """
    Get each amazon product field having a list of valid values (choices) for a given category
    """
    if category:
        category_data = get_categories()[category]
        feed_path = category_data["feed_path"]
    table = pd.read_excel(feed_path, sheet_name="Valid Values", skiprows=[0])
    fields_values = {
        field: options.dropna().tolist() for field, options in table.iteritems()
    }
    return json.dumps(fields_values) if to_json else fields_values


def get_fields(*, category="", feed_path="", to_json=False):
    """
    Get all amazon product fields and their data for a given category
    """
    if category:
        category_data = get_categories()[category]
        category_id = category_data["category_id"]
        feed_path = category_data["feed_path"]
    data_def = pd.read_excel(feed_path, sheet_name="Data Definitions", skiprows=[0])
    options = get_valid_fields_values(feed_path=feed_path)
    fields = []
    group_name = ""
    for row_num, (group, field, required) in data_def[
        ["Group Name", "Field Name", "Required?"]
    ].iterrows():
        if isinstance(group, str):
            group_name = group.split("-")[0].strip()
        else:
            fields.append(
                {
                    "group_name": group_name,
                    "name": field,
                    "category_id": category_id,
                    "required": required,
                    "options": options.get(field, []),
                }
            )
    return json.dumps(fields) if to_json else fields


def _get_nodes_files_paths(category="", nodes_files_paths=[]):
    """
    Get file paths of browse tree files for a given category
    """
    if category and nodes_files_paths:
        raise AttributeError("Нужно задать либо категорию, либо список путей к файлам")
    if category:
        return get_categories()[category]["nodes_files_paths"]
    return nodes_files_paths


def get_browse_nodes(*, category="", nodes_files_paths=[], to_json=False):
    """
    Get all browse nodes (subcategories) of a given category
    """
    if category:
        category_data = get_categories()[category]
        category_id = category_data["category_id"]
        nodes_files_paths = category_data["nodes_files_paths"]
    nodes = [] if to_json else {}
    for file_path in nodes_files_paths:
        table = pd.read_excel(file_path, sheet_name=1)
        last_node_of_level = {}
        for num, row in table[["Node ID", "Node Path", "Query"]].iterrows():
            node_id, node_path, query = row.values
            try:
                query = str(query)
            except Exception:
                is_leaf = False
            else:
                is_leaf = True
            node_name = node_path.split("/")[-1]
            level = len(node_path.split("/"))
            last_node_of_level[level] = node_id
            parent_id = last_node_of_level[level - 1] if level > 1 else "-1"
            data = {
                "category_id": category_id,
                "node_id": node_id,
                "node_name": node_name,
                "node_path": node_path,
                "parent_id": parent_id,
                "level": level,
                "is_leaf": is_leaf,
            }
            if to_json:
                nodes.append(data)
            else:
                nodes[node_id] = data
    return json.dumps(nodes) if to_json else nodes


def save_categories(dest="amazon/product/fixtures/product_categories.json"):
    with open(dest, "w") as fw:
        fw.write(get_categories(to_json=True))


def save_browse_nodes(dest="amazon/product/fixtures/browse_nodes.json"):
    browse_nodes = {}
    for category in get_categories():
        browse_nodes[category] = json.loads(
            get_browse_nodes(category=category, to_json=True)
        )
    with open(dest, "w") as fw:
        fw.write(json.dumps(browse_nodes, indent=4))


def save_fields(dest="amazon/product/fixtures/fields.json"):
    fields = {}
    for category in get_categories():
        fields[category] = json.loads(get_fields(category=category, to_json=True))
    with open(dest, "w") as fw:
        fw.write(json.dumps(fields, indent=4))
