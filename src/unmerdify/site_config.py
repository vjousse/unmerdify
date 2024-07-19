import glob
from urllib.parse import urlparse


def get_config_files(
    site_config_dir: str, include_config_dir: bool = True
) -> list[str]:
    """Read the files from the site_config directory"""
    filenames: list[str] = []

    for file in glob.iglob(f"{site_config_dir}/*.txt", include_hidden=True):
        if include_config_dir:
            filenames.append(file)
        else:
            filenames.append(file.removeprefix(f"{site_config_dir}/"))

    return filenames


def load_site_config_for_host(config_files: list[str], host: str):
    print(f"-> Loading site config for {host}")


def load_site_config_for_url(config_files: list[str], url: str):
    parsed_uri = urlparse(url)
    load_site_config_for_host(config_files, parsed_uri.netloc)
