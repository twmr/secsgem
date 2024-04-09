#####################################################################
# s03f02.py
#
# (c) Copyright 2021, Benjamin Parzella. All rights reserved.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#####################################################################
"""Class for stream 03 function 02."""

from secsgem.secs.data_items import LOC, MF, MID
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS03F02(SecsStreamFunction):
    """Material status data.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS03F02
        {
            MF: B/A
            PARAMS: [
                {
                    LOC: B[1]
                    MID: A/B[80]
                }
                ...
            ]
        }

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS03F02()
        S3F2
          <L [2]
            None
            <L>
          > .

    Data Items:
        - :class:`MF <secsgem.secs.data_items.MF>`
        - :class:`LOC <secsgem.secs.data_items.LOC>`
        - :class:`MID <secsgem.secs.data_items.MID>`

    """

    _stream = 3
    _function = 2

    _data_format = [MF, [["PARAMS", LOC, "QUA", MID]]]

    _to_host = True
    _to_equipment = False

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
