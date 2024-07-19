import glob
from urllib.parse import urlparse
import re


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
    """
    The five filters config files can be of the form

    - .specific.domain.tld (for *.specific.domain.tld)
    - specific.domain.tld (for this specific domain)
    - .domain.tld (for *.domain.tld)
    - domain.tld (for domain.tld)
    """

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


def parse_site_config_file(config_file_path: str) -> dict | None:
    config = {}
    with open(config_file_path, "r") as file:
        while line := file.readline():
            line = line.strip()

            # skip comments, empty lines
            if line == "" or line.startswith("#"):
                continue

            # Split on ": "
            parts = re.split(r": ", line)

            # if the line doesn't respect the `command: value` format
            # skip it
            if not len(parts) == 2:
                print(f"skipping {line}")
                continue

            command = parts[0].strip()
            value = parts[1].strip()

            # strip_attr is now an alias for strip, for example:
            # strip_attr: //img/@srcset
            if "strip_attr" == command:
                command = "strip"

            # check for commands where we accept multiple statements
            if command in [
                "title",
                "body",
                "strip",
                "strip_id_or_class",
                "strip_image_src",
                "single_page_link",
                "next_page_link",
                "test_url",
                "find_string",
                "replace_string",
                "login_extra_fields",
                "native_ad_clue",
                "date",
                "author",
            ]:
                config.setdefault(command, []).append(value)

            # check for single statement commands that evaluate to true or false
            elif command in [
                "tidy",
                "prune",
                "autodetect_on_failure",
                "requires_login",
                "skip_json_ld",
            ]:
                config[command] = "yes" == value or "true" == value

            # check for single statement commands stored as strings
            elif command in [
                "parser",
                "login_username_field",
                "login_password_field",
                "not_logged_in_xpath",
                "login_uri",
                "src_lazy_load_attr",
            ]:
                config[command] = value

            # check for replace_string(find): replace
            elif command.endswith(")") and command.startswith("replace_string("):
                result = re.search(r"^replace_string\((.*)\)$", command)
                if result:
                    config.setdefault("find_string", []).append(result.group(1))
                    config.setdefault("replace_string", []).append(value)
    import json

    print(json.dumps(config, indent=4))
    return config if config != {} else None


def load_site_config_for_host(config_files: list[str], host: str):
    print(f"-> Loading site config for {host}")
    config_file = get_config_file_for_host(config_files, host)

    if config_file:
        print(f"-> Found config file, loading {config_file} config.")
        parse_site_config_file(config_file)
    else:
        print(f"-> No config file found for host {host}.")


def load_site_config_for_url(config_files: list[str], url: str):
    load_site_config_for_host(config_files, get_host_for_url(url))
