import argparse

from unmerdify import site_config

parser = argparse.ArgumentParser(
    description="Get the content, only the content: unenshittificator for the web"
)

parser.add_argument(
    "ftr_site_config_dir",
    type=str,
    help="The path to the https://github.com/fivefilters/ftr-site-config files.",
)


parser.add_argument(
    "url",
    type=str,
    help="The url you want to unmerdify.",
)


def main() -> int:
    args = parser.parse_args()

    print(args.ftr_site_config_dir)
    print(args.url)
    config_files = site_config.get_config_files(args.ftr_site_config_dir)
    site_config.load_site_config_for_url(config_files, args.url)

    return 0
