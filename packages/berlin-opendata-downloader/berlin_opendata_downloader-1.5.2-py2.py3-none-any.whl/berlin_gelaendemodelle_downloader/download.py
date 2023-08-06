import io
import os
import re
import zipfile
import requests

from tqdm import tqdm
from bs4 import BeautifulSoup
from click import BadParameter

from .file import save_files
from .constant import DATA_URL, GEOJSON_FILE_FORMAT
from .utils import file_content_2_data_frame, create_directories, compress_data_frame, data_frame_2_geo_data_frame, download_2_file_content



def get_subset_links() -> list:
    """
    Get list of links for subsets of data.

    Returns:
        list: list of URLs to the zipped subsets
    """

    site = requests.get(DATA_URL)
    soup = BeautifulSoup(site.content, features="html.parser")

    links = []

    for link in soup.find_all("a"):
        if "zip" in link.get("href"):
            links.append(link.get("href"))

    return links


def download_zip(zip_url: str) -> (str, str):
    """
    Args:
        zip_url (str): URL to a zip subset of the data

    Returns:
        (str, list): file name and content of the file that is included in the zip archiv

    Raises:
        HTTPError: Will be raised if the ``zip_url`` responsed a not 200 code
    """

    try:
        request = requests.get(zip_url)

    except Exception:
        raise requests.HTTPError(f"Could not get URL: {zip_url}")


    if request.status_code == 200:
        zip_file_bytes = io.BytesIO(request.content)
        zipped_sub_set = zipfile.ZipFile(zip_file_bytes)

        # Zip archives only contain a single file
        file_name = zipped_sub_set.namelist()[0]
        download_content = zipped_sub_set.read(file_name).decode("utf8")

        # fix not consistant file names if necessary
        if not re.match(r".*\d{3}_\d{4}\.txt", file_name):
            file_name = os.path.splitext(file_name)[0]
            file_name = f"{file_name[:3]}_{file_name[-4:]}.txt"

        return file_name, download_2_file_content(download_content)

    else:
        raise requests.HTTPError(f"Could not get URL: {zip_url}")


def download_data(download_path: str, keep_original: bool, compress: int, file_format: tuple):
    """
    Download and compress the ground level data of Berlin.
    
    Args:
        download_path (str): path to download directory
        keep_original (bool): indicates to keep the original txt files or not
        compress (int): size of square pixels for compression
        file_format (tuple): file formats to save the data
    
    Raises:
        click.BadParameter: for invalid parameter combinations
    """    

    # Set constraints
    if compress <= 0:
        keep_original = True

    # creats all necessary directories
    original_path, compressed_path = create_directories(download_path, keep_original, compress, file_format)
    links = get_subset_links()

    # Without compression: download and keep the original files.
    if compress <= 0:
        for link in tqdm(links):

            file_name, file_content = download_zip(link)
            save_files(download_path, file_name, file_content, None, file_format, keep_original)


    # With compression: download and compress the data. Only save the originals it ``--keep-original`` is set.
    elif 2000 % compress == 0:
        for link in tqdm(links):

            file_name, file_content = download_zip(link)

            data_frame = file_content_2_data_frame(file_content)
            compressed_data_frame = compress_data_frame(data_frame, compress)

            if GEOJSON_FILE_FORMAT in file_format:
                compressed_data_frame = data_frame_2_geo_data_frame(compressed_data_frame)

            save_files(download_path, file_name, file_content, compressed_data_frame, file_format, keep_original)

    else:
        raise BadParameter("Argument 'compress' have to divide 2000 without remainder.")