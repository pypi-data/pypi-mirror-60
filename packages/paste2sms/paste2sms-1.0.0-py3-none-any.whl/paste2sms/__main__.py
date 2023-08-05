# Copyright 2020 Louis Paternault
#
# This file is part of paste2sms.
#
# paste2sms is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# paste2sms is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero Public License for more details.
#
# You should have received a copy of the GNU Affero Public License
# along with paste2sms.  If not, see <http://www.gnu.org/licenses/>.

"""Main script for paste2sms."""

import argparse
import configparser
import importlib
import logging
import os
import subprocess
import tempfile

from xdg import BaseDirectory
import notify2
import pyperclip

from . import P2SException, VERSION

APPNAME = "paste2sms"
CONFIG = "paste2sms.conf"

LEVELS = {
    logging.CRITICAL: "Critical",
    logging.ERROR: "Error",
    logging.WARNING: "Warning",
    logging.INFO: "Info",
    logging.DEBUG: "Debug",
}


def get_config_file():
    """Search for a configuration file, and return its name."""
    for directory in BaseDirectory.xdg_config_dirs:
        filename = os.path.join(directory, CONFIG)
        if os.path.exists(filename):
            return filename
    raise P2SException("No configuration file found.", level=logging.ERROR)


def read_config():
    """Return configuration file (as a configparser.ConfigParser() object."""
    config = configparser.ConfigParser()
    config.read([get_config_file()])
    return config


def get_editor(config):
    """Return the command line to be used to run the editor."""
    try:
        return config["general"]["editor"]
    except KeyError:
        return None


def get_content(config):
    """Edit content from clipboard.

    Open a file containing the clipboard content, and edit it. When
    user closes the editor, return the file content.
    """
    with tempfile.TemporaryDirectory() as tempdir:
        filename = os.path.join(tempdir, "message.txt")
        with open(filename, "w") as temp:
            temp.write(pyperclip.paste())

        editor = get_editor(config)
        if editor is not None:
            try:
                editor = editor.format(filename)
            except:
                raise P2SException(
                    "Editor configuration option is invalid.", level=logging.ERROR
                )

            try:
                subprocess.check_call(editor, shell=True)
            except subprocess.CalledProcessError as error:
                raise P2SException(str(error), level=logging.ERROR)

        with open(filename, "r") as temp:
            return temp.read().strip()


def send_sms(content, *, config):
    """Delegate SMS sending using the provider given in configuration."""
    try:
        provider = config["general"]["provider"]
    except KeyError:
        raise P2SException(
            "No cellphone provider given in configuration file.", level=logging.ERROR
        )
    module = importlib.import_module(f".provider.{provider}", __package__)
    return module.send_sms(content, config=config[f"provider:{provider}"])


def notify(message=None, *, level=logging.INFO):
    """Display a notification."""
    notify2.init(APPNAME)

    if message is None:
        message = "SMS sent successfully."
    else:
        message = "{}: {}".format(LEVELS.get(level, logging.INFO), message,)

    notify2.Notification(summary=message,).show()


def commandline_parser():
    """Build and return the command line parser."""
    parser = argparse.ArgumentParser(
        prog=__package__,
        description="Send clipboard content as a SMS.",
        epilog=(
            "This command line arguments has no options (besides the obligatory "
            "--help and --version): it is meant to be used as a graphical tool, "
            "and that's all. But this might change in the future…"
        ),
    )
    parser.add_argument(
        "--version", action="version", version="%(prog)s {}".format(VERSION)
    )
    return parser


def main():
    """Main function."""
    logging.basicConfig(level=logging.INFO)

    try:
        # Parse command line arguments
        commandline_parser().parse_args()

        # Read configuration file
        config = read_config()

        # Edit message
        content = get_content(config)
        if not content:
            raise P2SException("Message is empty. No SMS sent.", level=logging.WARNING)

        # Send message
        return_message = send_sms(content, config=config)

        # Notify user
        notify(return_message)

    except P2SException as error:
        logging.log(level=error.level, msg=str(error))
        notify(str(error), level=error.level)


if __name__ == "__main__":
    main()
