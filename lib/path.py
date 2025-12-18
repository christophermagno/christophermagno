"""
Path manipulation module.
"""

from pathlib import Path
import logging
import shutil
import chardet

from . import logger

log = logging.getLogger(__name__)


def get_project_dir():
    """
    Get the project directory (the directory of the project)
    """
    return Path().cwd()

def get_project_name():
    """
    Get the project name (the directory name of the project)
    """
    return get_project_dir().name


def detect_encoding(file_path):
    """
    Detects encoding of file to ensure proper encoding when reading files for Pandas

    :param file_path: Path to check encoding
    :return: encoding of file
    """
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    result = chardet.detect(raw_data)
    return result['encoding']

def get_cleaned_path(path, suffix='CLEAN', mkdirs=True):
    """
    Helper function to quickly create a "cleaned" file path.
    # TODO: Need to accomdate different extension types

    :param path: Path to messy data file
    :param suffix: Suffix to append to file path
    :param mkdirs: Whether to create the directory if it doesn't exist
    :return: Path to cleaned file
    """
    path = Path(path)
    if mkdirs:
        path.parent.mkdir(parents=True, exist_ok=True)
    return path.parent.joinpath(str(path.stem) + f'_{suffix}' + str(path.suffix))

def _source_control(path, pad=None, directory='_source_control'):
    """
    Not used. Create local source control of file.

    :param path:
    :param pad:
    :param directory:
    :return:
    """

    path = Path(path)

    pad = pad or '04'
    _fmt_string = '{}.{:' + pad + 'd}{}'

    file_stem = path.stem
    file_ext = path.suffix
    source_control_data_path = path.parent / directory / file_stem

    log.debug('file_stem: {}'.format(file_stem))
    log.debug('file_ext: {}'.format(file_ext))
    log.debug('source_control_data_path: {}'.format(source_control_data_path))

    # Create the source controlled directory (for the specific file) if it doesn't exist
    source_control_data_path.mkdir(parents=True, exist_ok=True)

    # Get files in source-control dir
    fs = [f for f in source_control_data_path.iterdir() if f.is_file() and f.stem.startswith(file_stem)]

    # Create the new source controlled path
    source_control_file_path = source_control_data_path / _fmt_string.format(file_stem, len(fs) + 1, file_ext)
    log.debug('source_control_file_path: {}'.format(source_control_file_path))

    # Make the move
    shutil.copy(path, source_control_file_path)

    return source_control_file_path