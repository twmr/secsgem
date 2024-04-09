#####################################################################
# loc.py
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
"""LOC data item."""

from .. import variables
from .base import DataItemBase


class LOC(DataItemBase, variables.Binary):
    """Machine material location code.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Used In Function**
        - :class:`SecsS03F02 <secsgem.secs.functions.SecsS03F02>`

    """

    __count__ = 1
