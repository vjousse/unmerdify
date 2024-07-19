from unmerdify import site_config


def test_get_config_files(site_config_dir):
    full_files = site_config.get_config_files(site_config_dir)

    assert len(full_files) == 2

    files = site_config.get_config_files(site_config_dir, include_config_dir=False)

    assert files == [".wikipedia.org.txt", "blast-info.fr.txt"]


def test_get_possible_config_files_for_host():
    assert site_config.get_possible_config_file_names_for_host(
        "vincent.jousse.org"
    ) == [
        ".vincent.jousse.org.txt",
        "vincent.jousse.org.txt",
        ".jousse.org.txt",
        "jousse.org.txt",
    ]
    assert site_config.get_possible_config_file_names_for_host("en.wikipedia.org") == [
        ".en.wikipedia.org.txt",
        "en.wikipedia.org.txt",
        ".wikipedia.org.txt",
        "wikipedia.org.txt",
    ]

    assert site_config.get_possible_config_file_names_for_host("blast-info.fr") == [
        ".blast-info.fr.txt",
        "blast-info.fr.txt",
    ]


def test_get_config_file_for_host(site_config_dir):
    files = site_config.get_config_files(site_config_dir, include_config_dir=False)

    config_file = site_config.get_config_file_for_host(files, "en.wikipedia.org")

    assert config_file == ".wikipedia.org.txt"

    config_file = site_config.get_config_file_for_host(files, "unknown.tld")

    assert config_file is None

    files = site_config.get_config_files(site_config_dir, include_config_dir=True)

    config_file = site_config.get_config_file_for_host(files, "en.wikipedia.org")

    assert config_file.endswith("/.wikipedia.org.txt")
