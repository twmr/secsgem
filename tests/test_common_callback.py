#####################################################################
# test_common_callback.py
#
# (c) Copyright 2016, Benjamin Parzella. All rights reserved.
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

import unittest.mock

import secsgem.common


class TestCallbackHandler(unittest.TestCase):
    def testRegisterCallback(self):
        f = unittest.mock.Mock()

        callbackHandler = secsgem.common.CallbackHandler()

        callbackHandler.test = f

        assert "test" in callbackHandler._callbacks
        assert callbackHandler._callbacks["test"] == f

    def testDoubleRegisterCallback(self):
        f1 = unittest.mock.Mock()
        f2 = unittest.mock.Mock()

        callbackHandler = secsgem.common.CallbackHandler()

        callbackHandler.test = f1
        callbackHandler.test = f2

        assert "test" in callbackHandler._callbacks
        assert callbackHandler._callbacks["test"] == f2

    def testUnregisterCallback(self):
        f = unittest.mock.Mock()

        callbackHandler = secsgem.common.CallbackHandler()

        callbackHandler.test = f

        assert "test" in callbackHandler._callbacks
        assert callbackHandler._callbacks["test"] == f

        callbackHandler.test = None

        assert "test" not in callbackHandler._callbacks

    def testUnregisterUnregisteredCallback(self):
        callbackHandler = secsgem.common.CallbackHandler()

        callbackHandler.test = None

        assert "test" not in callbackHandler._callbacks

    def testInWithCallback(self):
        f = unittest.mock.Mock()

        callbackHandler = secsgem.common.CallbackHandler()

        callbackHandler.test = f

        assert "test" in callbackHandler

    def testInWithDelegate(self):
        c = unittest.mock.Mock()

        callbackHandler = secsgem.common.CallbackHandler()
        callbackHandler.target = c

        assert "test" in callbackHandler

    def testNotIn(self):
        callbackHandler = secsgem.common.CallbackHandler()

        assert "test" not in callbackHandler

    def testCallWithCallback(self):
        f = unittest.mock.Mock()
        f.return_value = "testvalue"

        callbackHandler = secsgem.common.CallbackHandler()

        callbackHandler.test = f

        assert callbackHandler.test(self, "data") == "testvalue"

        f.assert_called_once_with(self, "data")

    def testCallWithDelegate(self):
        c = unittest.mock.Mock()
        c._on_test.return_value = "testvalue"

        callbackHandler = secsgem.common.CallbackHandler()
        callbackHandler.target = c

        callbackHandler.test(self, "data")

        c._on_test.assert_called_once_with(self, "data")

    def testCallWithNone(self):
        callbackHandler = secsgem.common.CallbackHandler()

        assert callbackHandler.test(self, "data") is None

    def testIteration(self):
        f = unittest.mock.Mock()
        f.return_value = "testvalue"

        callbackHandler = secsgem.common.CallbackHandler()

        callbackHandler.test = f

        for _callback in callbackHandler:
            pass
