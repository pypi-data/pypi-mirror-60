import os

def get_regular_path(file_location: str):
    return os.path.abspath(
        os.path.expanduser(file_location)
    )

def is_acceptable_file(file_location: str) -> bool:

    return os.path.exists(get_regular_path(file_location))
