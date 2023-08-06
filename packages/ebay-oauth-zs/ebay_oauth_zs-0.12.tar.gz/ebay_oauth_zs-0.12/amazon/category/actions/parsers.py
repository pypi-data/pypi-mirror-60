import json
import os


def get_categories(root_dir="amazon/data/feed_templates/categories/", to_json=False):
    """
    Get all amazon product categories (not browse nodes)
    """
    categories = [] if to_json else {}
    for category_id, cat_dir in enumerate(os.listdir(root_dir)):
        if os.path.isdir(os.path.join(root_dir, cat_dir)):
            dir_path = os.path.join(root_dir, cat_dir)
            feed_path = ""
            nodes_files_paths = []
            for file in os.listdir(dir_path):
                file_path = os.path.join(dir_path, file)
                if not file_path.endswith("#"):
                    if "_feed" in file:
                        feed_path = file_path
                    else:
                        nodes_files_paths.append(file_path)
            data = {
                "category_id": category_id,
                "dir_path": dir_path,
                "feed_path": feed_path,
                "nodes_files_paths": nodes_files_paths,
            }
            if to_json:
                categories.append(
                    {"name": cat_dir, **data,}
                )
            else:
                categories[cat_dir] = data
    return json.dumps(categories) if to_json else categories
