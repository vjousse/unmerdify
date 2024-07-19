from unmerdify import site_config


def test_get_config_files(site_config_dir):
    full_files = site_config.get_config_files(site_config_dir)

    assert len(full_files) == 2

    files = site_config.get_config_files(site_config_dir, include_config_dir=False)

    assert files == [".wikipedia.org.txt", "blast-info.fr.txt"]
