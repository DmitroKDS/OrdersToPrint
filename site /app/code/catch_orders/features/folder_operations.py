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
        makedirs(folder, exist_ok=True)


def delete(folders: str|list) -> None:
    """
    Delete a folder/folders if it/they exists
    """
    if isinstance(folders, str):
        folders = [folders]

    for folder in folders:
        if path.exists(folder):
            try:
                rmtree(folder)
            except Exception as e:
                print(f"Failed to delete folder '{folder}': {e}")