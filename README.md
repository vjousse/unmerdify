# `unmerdify`

Get the content, only the content: **unenshittificator** for the web.

# Installation

## `ftr-site-config`

First you will need to clone https://github.com/fivefilters/ftr-site-config locally (it contains the rules needed for this code to work).

## Using `rye`

Be sure to have [`rye`](https://rye.astral.sh/) installed, then:

    rye sync
    rye run unmerdify /path/to/ftr-site-config https://en.wikipedia.org/wiki/Metallica

Why `rye`? Because after using `cargo` for Rust, I'm now tired of using broken Python version management. `requirements.txt` sucks, managing multiple venvs sucks, managing multiple Python versions sucks, using `pyproject.toml` and `rye` is the way to go. If you still want to manage all this mess yourself, I'll try to keep a `requirements.txt` file up to date.

## Using `pip`

Manage your Python version, your virtualenv the way you want to and install the requirements.

    pip install -r requirements.txt
    python src/unmerdify /path/to/ftr-site-config https://en.wikipedia.org/wiki/Metallica

# Tests

    pytest

# Useful links

- Site configs: https://github.com/fivefilters/ftr-site-config
- Testing reports of the five filters rules: https://siteconfig.fivefilters.org/test/
- PHP code using the fivefilters files: https://github.com/j0k3r/graby/blob/1281bf3d7045d2f2682d1af6ba3715e492184e9a/src/Extractor/ContentExtractor.php#L142

# Ideas

Should we clean urls in the parsed html? https://github.com/ClearURLs/Rules
