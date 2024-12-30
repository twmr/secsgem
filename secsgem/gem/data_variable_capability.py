#####################################################################
# data_variable_capability.py
#
# (c) Copyright 2023, Benjamin Parzella. All rights reserved.
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
"""Data Value capability."""

from __future__ import annotations

import typing

from .capability import Capability
from .handler import GemHandler

if typing.TYPE_CHECKING:
    import secsgem.secs

    from .data_variable import DataVariable


class DataVariableCapability(GemHandler, Capability):
    """Data Value capability on GEM equipment."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize capability."""
        super().__init__(*args, **kwargs)

        self.__data_variables: dict[int | str, DataVariable] = {}

    @property
    def _data_variables(self) -> dict[int | str, DataVariable]:
        """Get list of the data values.

        Returns:
            Data variable list

        """
        return self.__data_variables

    @property
    def data_variables(self) -> dict[int | str, DataVariable]:
        """Get list of the data values.

        Returns:
            Data variablelist

        """
        return self._data_variables

    def on_dv_value_request(
        self,
        _data_variable_id: secsgem.secs.variables.Base,
        data_variable: DataVariable,
    ) -> secsgem.secs.variables.Base:
        """Get the data value depending on its configuation.

        Override in inherited class to provide custom data value request handling.

        Args:
            data_variable_id: Id of the data value encoded in the corresponding type
            data_variable: The data value requested

        Returns:
            The value encoded in the corresponding type

        """
        return data_variable.value_type(data_variable.value)

    def _get_dv_value(self, data_variable: DataVariable) -> secsgem.secs.variables.Base:
        """Get the data value depending on its configuation.

        Args:
            data_variable: The data value requested

        Returns:
            The value encoded in the corresponding type

        """
        if data_variable.use_callback:
            return self.on_dv_value_request(data_variable.id_type(data_variable.dvid), data_variable)

        return data_variable.value_type(data_variable.value)
