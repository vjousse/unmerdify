import argparse

from unmerdify import site_config

parser = argparse.ArgumentParser(description="Check ftr site config")

parser.add_argument(
    "ftr_site_config_dir",
    type=str,
    help="The path to the https://github.com/fivefilters/ftr-site-config files.",
)


def main():
    args = parser.parse_args()

    print(args.ftr_site_config_dir)
    config_files = site_config.get_config_files(args.ftr_site_config_dir)

    for config_file in config_files:
        site_config.parse_site_config_file(config_file)

    return 0
