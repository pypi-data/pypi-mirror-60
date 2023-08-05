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

"""Send content of clipboard as a SMS."""

from dataclasses import dataclass
import logging

VERSION = "1.0.0"


@dataclass
class P2SException(Exception):
    """Generic exception to be nicely catched and displayed to the user."""

    message: str
    level: int = logging.INFO
