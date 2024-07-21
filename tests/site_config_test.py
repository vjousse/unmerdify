from unmerdify import site_config

import logging

LOGGER = logging.getLogger(__name__)


def test_get_config_files(site_config_dir):
    full_files = site_config.get_config_files(site_config_dir)

    assert len(full_files) == 3

    files = site_config.get_config_files(site_config_dir, include_config_dir=False)

    assert files == [".wikipedia.org.txt", "blast-info.fr.txt", ".test.com.txt"]


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


def test_parse_site_config_file(test_site_config_path, caplog):
    config = site_config.parse_site_config_file(test_site_config_path)
    assert config == {
        "title": ["//h1[@id='firstHeading']"],
        "body": ["//div[@id = 'bodyContent']"],
        "strip_id_or_class": ["editsection", "vertical-navbox"],
        "strip": [
            "//*[@id='toc']",
            "//div[@id='catlinks']",
            "//div[@id='jump-to-nav']",
            "//div[@class='thumbcaption']//div[@class='magnify']",
            "//table[@class='navbox']",
            "//div[@class='dablink']",
            "//div[@id='contentSub']",
            "//table[contains(@class, 'metadata')]",
            "//*[contains(@class, 'noprint')]",
            "//span[@class='noexcerpt']",
            "//math",
        ],
        "author": [
            "substring-after( //p[@class='article-details__author-by']/text() , 'By: ')"
        ],
        "wrap_in": [
            {"h2": "//span[@class='subhead']"},
            {"i": "//p[@class='bio']"},
            {"i": "//p[@class='copyright']"},
        ],
        "http_header": [{"user-agent": "Mozilla/5.2"}],
        "find_string": [',"storylineText":', "to post comments)): ", ',"test)": '],
        "replace_string": [',"value":', "</div>", ',"value": and:'],
        "if_page_contains": {
            "//link[@rel=\"canonical\" and contains(@href, '_story.html')]": {
                "single_page_link": 'concat(substring-before(//link[@rel="canonical"]/@href, "_story.html"), "_print.html?noredirect=on")'
            }
        },
        "prune": False,
        "tidy": False,
        "test_url": [
            "http://en.wikipedia.org/wiki/Christopher_Lloyd",
            "https://en.wikipedia.org/wiki/Ronnie_James_Dio",
            "https://en.wikipedia.org/wiki/Metallica",
        ],
    }

    assert "unknown line format for line `nstnrs`" in caplog.text
    assert "unknown command name for line `unknown_command: value`" in caplog.text
