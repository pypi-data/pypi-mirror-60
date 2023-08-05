import uuid


def get_unique_name(filename):
    extension = filename.split(
        "."
    ).pop()  # в случае файла может не быть расширения? исполльзовать os.path.splitext?
    return f"{uuid.uuid4()}.{extension}"  # не видел, чтобы uuid использовалось в качестве alt (хранить исходное имя?)


# обобщить нижележащие функции?
def get_product_image_upload_path(instance, filename):
    return f"images/{get_unique_name(filename)}"


def get_marketplace_icon_upload_path(instance, filename):
    return f"icons/{get_unique_name(filename)}"


def get_support_file_upload_path(instance, filename):
    return f"support_files/{get_unique_name(filename)}"
