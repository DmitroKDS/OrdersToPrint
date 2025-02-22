from os import makedirs, path
from shutil import rmtree

def create(folders: str|list) -> None:
    """
    Create a folder/folders if it/they is/are exist remake it/they
    """
    delete(folders)

    if isinstance(folders, str):
        folders = [folders]

    for folder in folders:
        makedirs(folder)


def delete(folders: str|list) -> None:
    """
    Delete a folder/folders if it/they exists
    """
    if isinstance(folders, str):
        folders = [folders]

    for folder in folders:
        if path.exists(folder):
            rmtree(folder)