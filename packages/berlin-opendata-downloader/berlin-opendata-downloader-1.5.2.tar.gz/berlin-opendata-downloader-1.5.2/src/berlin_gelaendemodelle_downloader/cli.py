import click

from .download import download_data
from .constant import COMPRESS_HELP, KEEP_ORIGIGNAL_HELP, COMPRESS_DEFAULT, SUPPORTED_FILE_FORMATS_DEFAULT, SUPPORTED_FILE_FORMATS_HELP, SUPPORTED_FILE_FORMATS_CHOICE, GEOJSON_FILE_FORMAT



@click.group()
def cli():
    """
    Entrypoint of CLI implementation.
    """


@cli.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument("download-path", type=click.Path(exists=True, dir_okay=True, writable=True))
@click.option("--keep-original", type=bool, is_flag=True, help=KEEP_ORIGIGNAL_HELP)
@click.option("--compress", type=int, default=COMPRESS_DEFAULT, help=COMPRESS_HELP)
@click.option("--file-format", type=click.Choice(SUPPORTED_FILE_FORMATS_CHOICE, case_sensitive=True), default=SUPPORTED_FILE_FORMATS_DEFAULT, help=SUPPORTED_FILE_FORMATS_HELP, multiple=True)
def download(download_path: str, keep_original: bool, compress: int, file_format: tuple):
    """
    Downloads height information of Berlin to DOWNLOAD-PATH.
    """

    download_data(download_path=download_path, keep_original=keep_original, compress=compress, file_format=file_format)
