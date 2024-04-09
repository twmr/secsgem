#####################################################################
# mf.py
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
"""MF data item."""

from .. import variables
from .base import DataItemBase


class MF(DataItemBase, variables.Dynamic):
    """Material format code.

    :Types:
       - :class:`Binary <secsgem.secs.variables.Binary>`
       - :class:`String <secsgem.secs.variables.String>`

    **Values**
        +-------+-----------------+----------------------------------------------------------+
        | Value | Description     | Constant                                                 |
        +=======+=================+==========================================================+
        | 1     | xxx             | :const:`secsgem.secs.data_items.MF.QUANTITIES_IN_WAFERS` |
        +-------+-----------------+----------------------------------------------------------+
        | 15-63 | Reserved, error |                                                          |
        +-------+-----------------+----------------------------------------------------------+

    **Used In Function**
        - :class:`SecsS03F02 <secsgem.secs.functions.SecsS03F02>`

    """

    __allowedtypes__ = [variables.Binary, variables.String]

    QUANTITIES_IN_WAFERS = 1
