import glob
import re
from dataclasses import dataclass
from urllib.parse import urlparse

import logging

LOGGER = logging.getLogger(__name__)


@dataclass
class Command:
    """Class for keeping track of a command item."""

    name: str
    accept_multiple_values: bool = False
    is_bool: bool = False
    xpath_value: bool = False
    has_capture_group: bool = False
    special_command: bool = False


COMMANDS: list[Command] = [
    Command("author", accept_multiple_values=True),
    Command("autodetect_on_failure", is_bool=True),
    Command("body", accept_multiple_values=True),
    Command("date", accept_multiple_values=True),
    Command("find_string", accept_multiple_values=True),
    Command("http_header", has_capture_group=True, special_command=True),
    Command("if_page_contains", special_command=True),
    Command("login_extra_fields", accept_multiple_values=True),
    Command("login_password_field"),
    Command("login_uri"),
    Command("login_username_field"),
    Command("native_ad_clue", accept_multiple_values=True),
    Command("next_page_link", accept_multiple_values=True),
    Command("not_logged_in_xpath"),
    Command("parser"),
    Command("prune", is_bool=True),
    Command("replace_string", has_capture_group=True, accept_multiple_values=True),
    Command("requires_login", is_bool=True),
    Command("src_lazy_load_attr"),
    Command("single_page_link", accept_multiple_values=True),
    Command("skip_json_ld", is_bool=True),
    Command("strip", accept_multiple_values=True),
    Command("strip_id_or_class", accept_multiple_values=True),
    Command("strip_image_src", accept_multiple_values=True),
    Command("test_url", accept_multiple_values=True),
    Command("tidy", is_bool=True),
    Command("title", accept_multiple_values=True),
    Command("wrap_in", has_capture_group=True, special_command=True),
]

COMMANDS_PER_NAME: dict[str, Command] = {
    COMMANDS[i].name: COMMANDS[i] for i in range(0, len(COMMANDS))
}


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
        previous_command = None
        while line := file.readline():
            line = line.strip()

            # skip comments, empty lines
            if line == "" or line.startswith("#"):
                continue

            command_name = None
            command_value = None
            pattern = re.compile(r"^([a-z_]+)(?:\((.*)\))*:[ ]*(.*)$", re.I)

            result = pattern.search(line)

            if not result:
                logging.error(
                    f"-> 🚨 ERROR: unknown line format for line `{line}`. Skipping."
                )
                continue

            command_name = result.group(1).lower()
            command_arg = result.group(2)
            command_value = result.group(3)

            # strip_attr is now an alias for strip, for example:
            # strip_attr: //img/@srcset
            if "strip_attr" == command_name:
                command_name = "strip"

            command = COMMANDS_PER_NAME.get(command_name)

            if command is None:
                logging.error(
                    f"-> 🚨 ERROR: unknown command name for line `{line}`. Skipping."
                )
                continue

            # Check for commands where we accept multiple statements but we don't have args provided
            # It handles `replace_string: value` and not `replace_string(test): value`
            if (
                command.accept_multiple_values
                and command_arg is None
                and not command.special_command
            ):
                config.setdefault(command_name, []).append(command_value)
            # Single value command that should evaluate to a bool
            elif command.is_bool and not command.special_command:
                config[command_name] = "yes" == command_value or "true" == command_value
            # handle replace_string(test): value
            elif command.name == "replace_string" and command_arg is not None:
                config.setdefault("find_string", []).append(command_arg)
                config.setdefault("replace_string", []).append(command_value)
            # handle http_header(user-agent): Mozilla/5.2
            elif command.name == "http_header" and command_arg is not None:
                config.setdefault("http_header", []).append(
                    {command_arg: command_value}
                )
            # handle if_page_contains: Xpath value
            elif command.name == "if_page_contains":
                # Previous command should be applied only if this expression is true
                previous_command_value = config[previous_command.name]

                # Move the previous command into the "if_page_contains" command
                if (
                    previous_command.accept_multiple_values
                    and len(previous_command_value) > 0
                ):
                    config.setdefault("if_page_contains", {})[command_value] = {
                        previous_command.name: previous_command_value.pop()
                    }

                # Remove the entire key entry if the values are now empty
                if len(previous_command_value) == 0:
                    config.pop(previous_command.name)

            # handle if_page_contains: Xpath value
            elif command.name == "wrap_in":
                config.setdefault("wrap_in", []).append({command_arg: command_value})

            else:
                config[command_name] = command_value

            previous_command = command

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
