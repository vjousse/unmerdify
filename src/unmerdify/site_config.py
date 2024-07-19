import glob
from urllib.parse import urlparse


def get_config_files(
    site_config_dir: str, include_config_dir: bool = True
) -> list[str]:
    """
    Read the *.txt files from the site_config directory and returns the file list.

    Parameters:
        site_config_dir (str): The path to the directory containing the config files
        include_config_dir (bool): Should the config_dir be included in the returned list

    Returns:
        filenames (list[str]): The list of filenames found with the .txt extension
    """
    filenames: list[str] = []

    for file in glob.iglob(f"{site_config_dir}/*.txt", include_hidden=True):
        if include_config_dir:
            filenames.append(file)
        else:
            filenames.append(file.removeprefix(f"{site_config_dir}/"))

    return filenames


def get_host_for_url(url: str) -> str:
    parsed_uri = urlparse(url)
    return parsed_uri.netloc


def get_possible_config_file_names_for_host(
    host: str, file_extension: str = ".txt"
) -> list[str]:
    parts = host.split(".")

    if len(parts) < 2:
        raise ValueError(
            "The host must be of the form `host.com`. It seems that there is no dot in your host"
        )

    tld = parts.pop()
    domain = parts.pop()

    first_possible_name = f"{domain}.{tld}{file_extension}"
    possible_names = [first_possible_name, f".{first_possible_name}"]

    # While we still have parts in the domain name, prepend the part
    # and create the 2 new possible names
    while len(parts) > 0:
        next_part = parts.pop()
        possible_name = f"{next_part}.{possible_names[-2]}"
        possible_names.append(possible_name)
        possible_names.append(f".{possible_name}")

    # Put the most specific file names first
    possible_names.reverse()

    return possible_names


def get_config_file_for_host(config_files: list[str], host: str) -> str | None:
    possible_config_file_names = get_possible_config_file_names_for_host(host)

    for config_file in config_files:
        for possible_config_file_name in possible_config_file_names:
            if config_file.endswith(possible_config_file_name):
                return config_file


def load_site_config_for_host(config_files: list[str], host: str):
    print(f"-> Loading site config for {host}")
    config_file = get_config_file_for_host(config_files, host)

    if config_file:
        print(f"-> Found config file, loading {config_file} config.")
    else:
        print(f"-> No config file found for host {host}.")


def load_site_config_for_url(config_files: list[str], url: str):
    load_site_config_for_host(config_files, get_host_for_url(url))
