# -*- encoding: utf-8 -*-

"""Retrieves secrets from AWS via credstash, and returns a dictionary.

  Typical usage:

  from credstash_envvar_helper import get_credstash_config
  config_dict = get_credstash_config(name.of.secret)

  DB_USER = config_dict.get('DB_USER', 'some.default.value')
  DB_PASS = config_dict.get('DB_PASS', 'some.default.value')
  # et cetera

  Using the credstash command-line tool to get and eval() secrets
  to set environment variables is very commmon in development.  This
  helper allows the same export-formatted secrets to be used in test
  and production by converting such secrets to a config dictionary.

  Where your code runs, that environment will need permission to get
  secrets out of AWS.  In development, that might be your credentials.
  In test or production, it might be via an IAM execution role.
"""

from __future__ import print_function
import sys

import credstash


def get_credstash_config(key):
    """Retrieves a single secret from AWS via credstash, assumes the
    string returned is a list of newline-separated export statements

    export FOO='some-hush-hush-info-here'
    export BAR='some-other-secret-here'

    and parses these lines into a configuration dictionary.

    Args:
        key: A string naming the credstash secret to retrieve, which
            can optionally include a version number.

    Returns:
        A dict with keys for each of of the environment variables
            described in the secret's contents.  The dict keys
            will be returned in upper case, as a convention.

        {'FOO': 'some-hush-hush-info-here'
         'BAR': 'some-other-secret-here'}

        Blank lines, lines that do not start with 'export ', and lines
        that do not contain '=' are ignored.

        The returned dictionary might be empty, so use safe methods
        to .get() the keys you were expecting to find in it.

    Raises:
        credstash.ItemNotFound: provided key not found by credstash
        SyntaxError: parsing of secret failed
        ValueError: parsing of secret failed
    """

    try:
        raw_secrets = credstash.getSecret(key)
    except credstash.ItemNotFound:
        raise

    # assume raw secret is a multiline string of export statements e.g.
    # export FOO=bar\nexport BAZ=goo
    try:
        # get the interesting, non-blank, parsable-looking lines into a list
        parsed_secrets = [
            line.replace("export ", "")
            for line in raw_secrets.split("\n")
            if line.startswith("export ") and "=" in line
        ]

        # parse those KEY=value lines into a dict, splitting only on first '='
        config_secrets = {}
        config_secrets = dict(line.split("=", 1) for line in parsed_secrets)

        # make sure all keys are uppercase
        upper_config_secrets = {}
        for k, val in config_secrets.items():
            upper_config_secrets[k.upper()] = val

    except (SyntaxError, ValueError):
        raise

    return upper_config_secrets


if __name__ == "__main__":
    print(get_credstash_config(sys.argv[1]))
