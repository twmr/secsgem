#####################################################################
# test_common_event.py
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

import logging
import unittest.mock

import pytest

import secsgem.common

log = logging.getLogger(__name__)


class TestEventProducer(unittest.TestCase):
    def testConstructor(self):
        producer = secsgem.common.EventProducer()

        assert producer._events == {}

    def testAddEvent(self):
        f = unittest.mock.Mock()

        producer = secsgem.common.EventProducer()

        producer.test += f

        assert "test" in producer

    def testRemoveEvent(self):
        f = unittest.mock.Mock()

        producer = secsgem.common.EventProducer()

        producer.test += f

        assert "test" in producer

        producer.test -= f

        assert "test" not in producer

    def testEventRepr(self):
        f = unittest.mock.Mock()

        producer = secsgem.common.EventProducer()

        producer.test += f

        log.info(producer.test)
        log.info(producer)

    def testJoinProducers(self):
        f1 = unittest.mock.Mock()
        f2 = unittest.mock.Mock()

        producer1 = secsgem.common.EventProducer()
        producer2 = secsgem.common.EventProducer()

        producer1.test1 += f1
        producer2.test2 += f2

        producer1 += producer2

        assert "test2" in producer1

    def testAddTarget(self):
        c = unittest.mock.Mock()

        producer = secsgem.common.EventProducer()

        producer.targets += c

        assert c in producer.targets

    def testRemoveTarget(self):
        c = unittest.mock.Mock()

        producer = secsgem.common.EventProducer()

        producer.targets += c

        assert c in producer.targets

        producer.targets -= c

        assert c not in producer.targets

    def testJoinProducersTargets(self):
        c1 = unittest.mock.Mock()
        c2 = unittest.mock.Mock()

        producer1 = secsgem.common.EventProducer()
        producer2 = secsgem.common.EventProducer()

        producer1.targets += c1
        producer2.targets += c2

        producer1 += producer2

        assert c2 in producer1.targets

    def testFire(self):
        f1 = unittest.mock.Mock()
        f2 = unittest.mock.Mock()
        c1 = unittest.mock.Mock()
        c2 = unittest.mock.Mock()

        producer = secsgem.common.EventProducer()

        producer.targets += c1
        producer.targets += c2
        producer.test += f1
        producer.test += f2

        producer.fire("test", "dummydata")

        f1.assert_called_once_with("dummydata")
        f2.assert_called_once_with("dummydata")
        c1._on_event_test.assert_called_once_with("dummydata")
        c2._on_event_test.assert_called_once_with("dummydata")
        c1._on_event.assert_called_once_with("test", "dummydata")
        c2._on_event.assert_called_once_with("test", "dummydata")

    def testInvalidTargetAssignment(self):
        test = 1

        producer = secsgem.common.EventProducer()

        with pytest.raises(AttributeError):
            producer.targets = test
