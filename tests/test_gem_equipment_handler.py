#####################################################################
# test_gem_equipment_handler.py
#
# (c) Copyright 2013-2016, Benjamin Parzella. All rights reserved.
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

import datetime
import threading
import unittest.mock

import pytest
from dateutil.parser import parse
from dateutil.tz import tzlocal
from mock_protocol import MockProtocol
from mock_settings import MockSettings
from test_gem_handler import GemHandlerPassiveGroup

import secsgem.gem
import secsgem.gem.control_state_machine
import secsgem.hsms
import secsgem.secs


class TestDataValue(unittest.TestCase):
    def testConstructorWithInt(self):
        dv = secsgem.gem.DataValue(
            123, "TestDataValue", secsgem.secs.variables.String, False, param1="param1", param2=2
        )

        assert dv.dvid == 123
        assert dv.name == "TestDataValue"
        assert dv.value_type == secsgem.secs.variables.String
        assert dv.use_callback is False
        assert dv.param1 == "param1"
        assert dv.param2 == 2

    def testConstructorWithStr(self):
        dv = secsgem.gem.DataValue(
            "DV123", "TestDataValue", secsgem.secs.variables.String, False, param1="param1", param2=2
        )

        assert dv.dvid == "DV123"
        assert dv.name == "TestDataValue"
        assert dv.value_type == secsgem.secs.variables.String
        assert dv.use_callback is False
        assert dv.param1 == "param1"
        assert dv.param2 == 2


class TestStatusVariable(unittest.TestCase):
    def testConstructorWithInt(self):
        sv = secsgem.gem.StatusVariable(
            123, "TestStatusVariable", "mm", secsgem.secs.variables.String, False, param1="param1", param2=2
        )

        assert sv.svid == 123
        assert sv.name == "TestStatusVariable"
        assert sv.unit == "mm"
        assert sv.value_type == secsgem.secs.variables.String
        assert sv.use_callback is False
        assert sv.param1 == "param1"
        assert sv.param2 == 2

    def testConstructorWithStr(self):
        sv = secsgem.gem.StatusVariable(
            "SV123", "TestStatusVariable", "mm", secsgem.secs.variables.String, False, param1="param1", param2=2
        )

        assert sv.svid == "SV123"
        assert sv.name == "TestStatusVariable"
        assert sv.unit == "mm"
        assert sv.value_type == secsgem.secs.variables.String
        assert sv.use_callback is False
        assert sv.param1 == "param1"
        assert sv.param2 == 2


class TestCollectionEvent(unittest.TestCase):
    def testConstructorWithInt(self):
        ce = secsgem.gem.CollectionEvent(123, "TestCollectionEvent", [123, "DV123"], param1="param1", param2=2)

        assert ce.ceid == 123
        assert ce.name == "TestCollectionEvent"
        assert ce.data_values == [123, "DV123"]
        assert ce.param1 == "param1"
        assert ce.param2 == 2

    def testConstructorWithStr(self):
        ce = secsgem.gem.CollectionEvent("CE123", "TestCollectionEvent", [123, "DV123"], param1="param1", param2=2)

        assert ce.ceid == "CE123"
        assert ce.name == "TestCollectionEvent"
        assert ce.data_values == [123, "DV123"]
        assert ce.param1 == "param1"
        assert ce.param2 == 2


class TestCollectionEventLink(unittest.TestCase):
    def testConstructor(self):
        ce = secsgem.gem.CollectionEvent(123, "TestCollectionEvent", [123, "DV123"])
        cel = secsgem.gem.CollectionEventLink(ce, [1000], param1="param1", param2=2)

        assert cel.collection_event == ce
        assert cel.enabled is False
        assert cel.reports == [1000]
        assert cel.param1 == "param1"
        assert cel.param2 == 2


class TestCollectionEventReport(unittest.TestCase):
    def testConstructorWithInt(self):
        cer = secsgem.gem.CollectionEventReport(123, [123, "DV123"], param1="param1", param2=2)

        assert cer.rptid == 123
        assert cer.vars == [123, "DV123"]
        assert cer.param1 == "param1"
        assert cer.param2 == 2

    def testConstructorWithStr(self):
        cer = secsgem.gem.CollectionEventReport("RPT123", [123, "DV123"], param1="param1", param2=2)

        assert cer.rptid == "RPT123"
        assert cer.vars == [123, "DV123"]
        assert cer.param1 == "param1"
        assert cer.param2 == 2


class TestEquipmentConstant(unittest.TestCase):
    def testConstructorWithInt(self):
        ec = secsgem.gem.EquipmentConstant(
            123, "TestEquipmentConstant", 0, 100, 50, "mm", secsgem.secs.variables.U4, False, param1="param1", param2=2
        )

        assert ec.ecid == 123
        assert ec.name == "TestEquipmentConstant"
        assert ec.min_value == 0
        assert ec.max_value == 100
        assert ec.default_value == 50
        assert ec.unit == "mm"
        assert ec.value_type == secsgem.secs.variables.U4
        assert ec.use_callback is False
        assert ec.param1 == "param1"
        assert ec.param2 == 2

    def testConstructorWithStr(self):
        ec = secsgem.gem.EquipmentConstant(
            "EC123",
            "TestEquipmentConstant",
            0,
            100,
            50,
            "mm",
            secsgem.secs.variables.U4,
            False,
            param1="param1",
            param2=2,
        )

        assert ec.ecid == "EC123"
        assert ec.name == "TestEquipmentConstant"
        assert ec.min_value == 0
        assert ec.max_value == 100
        assert ec.default_value == 50
        assert ec.unit == "mm"
        assert ec.value_type == secsgem.secs.variables.U4
        assert ec.use_callback is False
        assert ec.param1 == "param1"
        assert ec.param2 == 2


class TestAlarm(unittest.TestCase):
    def testConstructorWithInt(self):
        alarm = secsgem.gem.Alarm(
            123,
            "TestAlarm",
            "TestAlarmText",
            secsgem.secs.data_items.ALCD.PERSONAL_SAFETY | secsgem.secs.data_items.ALCD.EQUIPMENT_SAFETY,
            100025,
            200025,
            param1="param1",
            param2=2,
        )

        assert alarm.alid == 123
        assert alarm.name == "TestAlarm"
        assert alarm.text == "TestAlarmText"
        assert (
            alarm.code == secsgem.secs.data_items.ALCD.PERSONAL_SAFETY | secsgem.secs.data_items.ALCD.EQUIPMENT_SAFETY
        )
        assert alarm.ce_on == 100025
        assert alarm.ce_off == 200025
        assert alarm.param1 == "param1"
        assert alarm.param2 == 2

    def testConstructorWithStr(self):
        alarm = secsgem.gem.Alarm(
            "AL123",
            "TestAlarm",
            "TestAlarmText",
            secsgem.secs.data_items.ALCD.PERSONAL_SAFETY | secsgem.secs.data_items.ALCD.EQUIPMENT_SAFETY,
            100025,
            200025,
            param1="param1",
            param2=2,
        )

        assert alarm.alid == "AL123"
        assert alarm.name == "TestAlarm"
        assert alarm.text == "TestAlarmText"
        assert (
            alarm.code == secsgem.secs.data_items.ALCD.PERSONAL_SAFETY | secsgem.secs.data_items.ALCD.EQUIPMENT_SAFETY
        )
        assert alarm.ce_on == 100025
        assert alarm.ce_off == 200025
        assert alarm.param1 == "param1"
        assert alarm.param2 == 2


class TestRemoteCommand(unittest.TestCase):
    def testConstructorWithInt(self):
        rcmd = secsgem.gem.RemoteCommand(123, "TestRCMD", [], 100025, param1="param1", param2=2)

        assert rcmd.rcmd == 123
        assert rcmd.name == "TestRCMD"
        assert rcmd.params == []
        assert rcmd.ce_finished == 100025
        assert rcmd.param1 == "param1"
        assert rcmd.param2 == 2

    def testConstructorWithStr(self):
        rcmd = secsgem.gem.RemoteCommand("TEST_RCMD", "TestRCMD", [], 100025, param1="param1", param2=2)

        assert rcmd.rcmd == "TEST_RCMD"
        assert rcmd.name == "TestRCMD"
        assert rcmd.params == []
        assert rcmd.ce_finished == 100025
        assert rcmd.param1 == "param1"
        assert rcmd.param2 == 2


class TestGemEquipmentHandler(unittest.TestCase):
    def testControlInitialStateDefault(self):
        settings = MockSettings(MockProtocol)
        client = secsgem.gem.GemEquipmentHandler(settings)

        assert client.control_state.current == secsgem.gem.control_state_machine.ControlState.HOST_OFFLINE

    def testControlInitialStateEquipmentOffline(self):
        settings = MockSettings(MockProtocol)
        client = secsgem.gem.GemEquipmentHandler(settings, initial_control_state="EQUIPMENT_OFFLINE")

        assert client.control_state.current == secsgem.gem.control_state_machine.ControlState.EQUIPMENT_OFFLINE

    def testControlInitialStateHostOffline(self):
        settings = MockSettings(MockProtocol)
        client = secsgem.gem.GemEquipmentHandler(settings, initial_control_state="HOST_OFFLINE")

        assert client.control_state.current == secsgem.gem.control_state_machine.ControlState.HOST_OFFLINE
        assert client._get_control_state_id() == 3

    def testControlInitialStateOnline(self):
        settings = MockSettings(MockProtocol)
        client = secsgem.gem.GemEquipmentHandler(settings, initial_control_state="ONLINE")

        assert client.control_state.current == secsgem.gem.control_state_machine.ControlState.ONLINE_REMOTE
        assert client._get_control_state_id() == 5

    def testControlInitialStateOnlineLocal(self):
        settings = MockSettings(MockProtocol)
        client = secsgem.gem.GemEquipmentHandler(
            settings, initial_control_state="ONLINE", initial_online_control_state="LOCAL"
        )

        assert client.control_state.current == secsgem.gem.control_state_machine.ControlState.ONLINE_LOCAL

    def testControlRemoteToLocal(self):
        settings = MockSettings(MockProtocol)
        client = secsgem.gem.GemEquipmentHandler(settings, initial_control_state="ONLINE")

        assert client.control_state.current == secsgem.gem.control_state_machine.ControlState.ONLINE_REMOTE

        client.control_switch_online_local()

        assert client.control_state.current == secsgem.gem.control_state_machine.ControlState.ONLINE_LOCAL

    def testControlLocalToRemote(self):
        settings = MockSettings(MockProtocol)
        client = secsgem.gem.GemEquipmentHandler(
            settings, initial_control_state="ONLINE", initial_online_control_state="LOCAL"
        )

        assert client.control_state.current == secsgem.gem.control_state_machine.ControlState.ONLINE_LOCAL

        client.control_switch_online_remote()

        assert client.control_state.current == secsgem.gem.control_state_machine.ControlState.ONLINE_REMOTE

    def testControlOnlineToOffline(self):
        settings = MockSettings(MockProtocol)
        client = secsgem.gem.GemEquipmentHandler(
            settings, initial_control_state="ONLINE", initial_online_control_state="LOCAL"
        )

        assert client.control_state.current == secsgem.gem.control_state_machine.ControlState.ONLINE_LOCAL

        client.control_switch_offline()

        assert client.control_state.current == secsgem.gem.control_state_machine.ControlState.EQUIPMENT_OFFLINE

    def testSVcontrol_stateOnlineLocal(self):
        settings = MockSettings(MockProtocol)
        client = secsgem.gem.GemEquipmentHandler(
            settings, initial_control_state="ONLINE", initial_online_control_state="LOCAL"
        )

        assert client.control_state.current == secsgem.gem.control_state_machine.ControlState.ONLINE_LOCAL
        assert client._get_control_state_id() == 4


class TestGemEquipmentHandlerPassive(unittest.TestCase, GemHandlerPassiveGroup):
    __testClass = secsgem.gem.GemEquipmentHandler

    def setUp(self):
        assert self.__testClass is not None

        self.settings = MockSettings(MockProtocol)
        self.client = self.__testClass(self.settings)

        self.client.enable()

    def tearDown(self):
        self.client.disable()


class TestGemEquipmentHandlerPassiveControlState(unittest.TestCase):
    def setUp(self):
        self.settings = MockSettings(MockProtocol)

        self.client = secsgem.gem.GemEquipmentHandler(self.settings, initial_control_state="EQUIPMENT_OFFLINE")

        self.client.enable()

    def tearDown(self):
        self.client.disable()

    def establishCommunication(self):
        self.settings.protocol.simulate_connect()

        packet = self.settings.protocol.expect_message(function=13)

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS01F14([0]), packet.header.system
            )
        )

    def testControlConnect(self):
        self.establishCommunication()

        clientCommandThread = threading.Thread(
            target=self.client.control_switch_online,
            name="TestGemEquipmentHandlerPassiveControlState_testControlConnect",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=1)

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS01F02(), packet.header.system
            )
        )

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        assert self.client.control_state.current == secsgem.gem.control_state_machine.ControlState.ONLINE_REMOTE

    def testControlConnectDenied(self):
        self.establishCommunication()

        clientCommandThread = threading.Thread(
            target=self.client.control_switch_online,
            name="TestGemEquipmentHandlerPassiveControlState_testControlConnectDenied",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=1)

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS01F00(), packet.header.system
            )
        )

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        assert self.client.control_state.current == secsgem.gem.control_state_machine.ControlState.HOST_OFFLINE

    def testControlRequestOffline(self):
        self.establishCommunication()

        clientCommandThread = threading.Thread(
            target=self.client.control_switch_online,
            name="TestGemEquipmentHandlerPassiveControlState_testControlRequestOffline",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=1)

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS01F02(), packet.header.system
            )
        )

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        assert self.client.control_state.current == secsgem.gem.control_state_machine.ControlState.ONLINE_REMOTE

        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(secsgem.secs.functions.SecsS01F15(), system_id)
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 1
        assert packet.header.function == 16

        function = self.client.streams_functions.decode(packet)

        assert function.get() == 0

        assert self.client.control_state.current == secsgem.gem.control_state_machine.ControlState.HOST_OFFLINE

    def testControlRequestOnline(self):
        self.establishCommunication()

        clientCommandThread = threading.Thread(
            target=self.client.control_switch_online,
            name="TestGemEquipmentHandlerPassiveControlState_testControlRequestOnline",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=1)

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS01F02(), packet.header.system
            )
        )

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        assert self.client.control_state.current == secsgem.gem.control_state_machine.ControlState.ONLINE_REMOTE

        system_id = 1
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(secsgem.secs.functions.SecsS01F15(), system_id)
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 1
        assert packet.header.function == 16

        assert self.client.control_state.current == secsgem.gem.control_state_machine.ControlState.HOST_OFFLINE

        system_id = 1
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(secsgem.secs.functions.SecsS01F17(), system_id)
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 1
        assert packet.header.function == 18

        function = self.client.streams_functions.decode(packet)

        assert function.get() == 0

        assert self.client.control_state.current == secsgem.gem.control_state_machine.ControlState.ONLINE_REMOTE

    def testControlRequestOnlineWhileOnline(self):
        self.establishCommunication()

        clientCommandThread = threading.Thread(
            target=self.client.control_switch_online,
            name="TestGemEquipmentHandlerPassiveControlState_testControlRequestOnline",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=1)

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS01F02(), packet.header.system
            )
        )

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        assert self.client.control_state.current == secsgem.gem.control_state_machine.ControlState.ONLINE_REMOTE

        system_id = 1
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(secsgem.secs.functions.SecsS01F17(), system_id)
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 1
        assert packet.header.function == 18

        function = self.client.streams_functions.decode(packet)

        assert function.get() == 2

        assert self.client.control_state.current == secsgem.gem.control_state_machine.ControlState.ONLINE_REMOTE

    def setupTestStatusVariables(self, use_callback=False):
        self.client.status_variables.update(
            {
                10: secsgem.gem.StatusVariable(
                    10, "sample1, numeric SVID, U4", "meters", secsgem.secs.variables.U4, use_callback
                ),
                "SV2": secsgem.gem.StatusVariable(
                    "SV2", "sample2, text SVID, String", "chars", secsgem.secs.variables.String, use_callback
                ),
            }
        )

        self.client.status_variables[10].value = 123
        self.client.status_variables["SV2"].value = "sample sv"

    def sendSVNamelistRequest(self, svs=None):
        if svs is None:
            svs = []
        system_id = 1
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(secsgem.secs.functions.SecsS01F11(svs), system_id)
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 1
        assert packet.header.function == 12

        return self.client.streams_functions.decode(packet)

    def testStatusVariableNameListAll(self):
        self.setupTestStatusVariables()
        self.establishCommunication()

        function = self.sendSVNamelistRequest()

        SV2 = next((x for x in function if x[0].get() == "SV2"), None)

        assert SV2 is not None
        assert SV2[1].get() == "sample2, text SVID, String"
        assert SV2[2].get() == "chars"

        SV10 = next((x for x in function if x[0].get() == 10), None)

        assert SV10 is not None
        assert SV10[1].get() == "sample1, numeric SVID, U4"
        assert SV10[2].get() == "meters"

    def testStatusVariableNameListLimited(self):
        self.setupTestStatusVariables()
        self.establishCommunication()

        function = self.sendSVNamelistRequest(["SV2", 10])

        SV2 = function[0]

        assert SV2 is not None
        assert SV2[0].get() == "SV2"
        assert SV2[1].get() == "sample2, text SVID, String"
        assert SV2[2].get() == "chars"

        SV10 = function[1]

        assert SV10 is not None
        assert SV10[0].get() == 10
        assert SV10[1].get() == "sample1, numeric SVID, U4"
        assert SV10[2].get() == "meters"

    def testStatusVariableNameListInvalid(self):
        self.setupTestStatusVariables()
        self.establishCommunication()

        function = self.sendSVNamelistRequest(["asdfg"])

        SV = function[0]

        assert SV is not None
        assert SV[0].get() == "asdfg"
        assert SV[1].get() == ""
        assert SV[2].get() == ""

    def sendSVRequest(self, svs=None):
        if svs is None:
            svs = []
        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(secsgem.secs.functions.SecsS01F03(svs), system_id)
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 1
        assert packet.header.function == 4

        return self.client.streams_functions.decode(packet)

    def testStatusVariableAll(self):
        self.setupTestStatusVariables()
        self.establishCommunication()

        function = self.sendSVRequest()

        SV10 = next((x for x in function if x.get() == 123), None)
        assert SV10 is not None

        SV2 = next((x for x in function if x.get() == "sample sv"), None)
        assert SV2 is not None

    def testStatusVariableLimited(self):
        self.setupTestStatusVariables()
        self.establishCommunication()

        function = self.sendSVRequest(["SV2", 10])

        SV2 = function[0]

        assert SV2 is not None
        assert SV2.get() == "sample sv"

        SV10 = function[1]

        assert SV10 is not None
        assert SV10.get() == 123

    def testStatusVariableWithCallback(self):
        self.setupTestStatusVariables(True)
        self.establishCommunication()

        function = self.sendSVRequest(["SV2", 10])

        SV2 = function[0]

        assert SV2 is not None
        assert SV2.get() == "sample sv"

        SV10 = function[1]

        assert SV10 is not None
        assert SV10.get() == 123

    def testStatusVariableInvalid(self):
        self.setupTestStatusVariables()
        self.establishCommunication()

        function = self.sendSVRequest(["asdfg"])

        SV = function[0]

        assert SV is not None
        assert SV.get() == []

    def testStatusVariablePredefinedClock(self):
        self.establishCommunication()

        delta = datetime.timedelta(seconds=5)

        # timeformat 0
        function = self.sendECUpdate(
            [{"ECID": secsgem.gem.EquipmentConstantId.TIME_FORMAT.value, "ECV": secsgem.secs.variables.U4(0)}]
        )

        function = self.sendSVRequest([secsgem.gem.StatusVariableId.CLOCK.value])

        equ_time = function[0]
        now = datetime.datetime.now()

        assert equ_time is not None

        equ_datetime = datetime.datetime.strptime(equ_time.get(), "%y%m%d%H%M%S")

        assert now - delta < equ_datetime < now + delta

        # timeformat 1
        function = self.sendECUpdate(
            [{"ECID": secsgem.gem.EquipmentConstantId.TIME_FORMAT.value, "ECV": secsgem.secs.variables.U4(1)}]
        )

        function = self.sendSVRequest([secsgem.gem.StatusVariableId.CLOCK.value])

        equ_time = function[0]
        now = datetime.datetime.now()

        assert equ_time is not None

        equ_datetime = datetime.datetime.strptime(equ_time.get() + "000", "%Y%m%d%H%M%S%f")

        assert now - delta < equ_datetime < now + delta

        # timeformat 2
        function = self.sendECUpdate(
            [{"ECID": secsgem.gem.EquipmentConstantId.TIME_FORMAT.value, "ECV": secsgem.secs.variables.U4(2)}]
        )

        function = self.sendSVRequest([secsgem.gem.StatusVariableId.CLOCK.value])

        equ_time = function[0]
        now = datetime.datetime.now(tzlocal())

        assert equ_time is not None

        equ_datetime = parse(equ_time.get())

        assert now - delta < equ_datetime < now + delta

    def testStatusVariablePredefinedEventsEnabled(self):
        self.setupTestDataValues()
        self.setupTestCollectionEvents()
        self.establishCommunication()

        function = self.sendCEDefineReport()
        function = self.sendCELinkReport()
        function = self.sendCEEnableReport()

        function = self.sendSVRequest([secsgem.gem.StatusVariableId.EVENTS_ENABLED.value])

        assert function[0].get() == [50]

    def testStatusVariablePredefinedAlarmsEnabled(self):
        self.setupTestAlarms()
        self.establishCommunication()

        function = self.sendSVRequest([secsgem.gem.StatusVariableId.ALARMS_ENABLED.value])
        assert function[0].get() == []

        function = self.sendAlarmEnable()

        function = self.sendSVRequest([secsgem.gem.StatusVariableId.ALARMS_ENABLED.value])
        assert function[0].get() == [25]

    def testStatusVariablePredefinedAlarmsSet(self):
        self.setupTestAlarms()
        self.establishCommunication()

        function = self.sendSVRequest([secsgem.gem.StatusVariableId.ALARMS_SET.value])
        assert function[0].get() == []

        function = self.sendAlarmEnable()

        clientCommandThread = threading.Thread(
            target=self.client.set_alarm,
            args=(25,),
            name="TestGemEquipmentHandlerPassiveControlState_testStatusVariablePredefinedAlarmsSet",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=1)

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS05F02(secsgem.secs.data_items.ACKC5.ACCEPTED), packet.header.system
            )
        )

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        function = self.sendSVRequest([secsgem.gem.StatusVariableId.ALARMS_SET.value])
        assert function[0].get() == [25]

        clientCommandThread = threading.Thread(
            target=self.client.clear_alarm,
            args=(25,),
            name="TestGemEquipmentHandlerPassiveControlState_testStatusVariablePredefinedAlarmsSet",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=1)

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS05F02(secsgem.secs.data_items.ACKC5.ACCEPTED), packet.header.system
            )
        )

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        function = self.sendSVRequest([secsgem.gem.StatusVariableId.ALARMS_SET.value])
        assert function[0].get() == []

    def setupTestDataValues(self, use_callbacks=False):
        self.client.data_values.update(
            {
                30: secsgem.gem.DataValue(30, "sample1, numeric DV, U4", secsgem.secs.variables.U4, use_callbacks),
            }
        )

        self.client.data_values[30].value = 31337

    def setupTestCollectionEvents(self):
        self.client.collection_events.update(
            {
                50: secsgem.gem.CollectionEvent(50, "test collection event", [30]),
            }
        )

    def setupTestAlarms(self):
        self.client.collection_events.update(
            {
                100025: secsgem.gem.CollectionEvent(100025, "test alarm on", []),
                200025: secsgem.gem.CollectionEvent(200025, "test alarm off", []),
                100030: secsgem.gem.CollectionEvent(100030, "test alarm 2 on", []),
                200030: secsgem.gem.CollectionEvent(200030, "test alarm 2 off", []),
            }
        )
        self.client.alarms.update(
            {
                25: secsgem.gem.Alarm(
                    25,
                    "test alarm",
                    "test text",
                    secsgem.secs.data_items.ALCD.PERSONAL_SAFETY | secsgem.secs.data_items.ALCD.EQUIPMENT_SAFETY,
                    100025,
                    200025,
                ),
                30: secsgem.gem.Alarm(
                    30,
                    "test alarm 2",
                    "test text 2",
                    secsgem.secs.data_items.ALCD.PERSONAL_SAFETY | secsgem.secs.data_items.ALCD.EQUIPMENT_SAFETY,
                    100030,
                    200030,
                ),
            }
        )

    def setupTestRemoteCommands(self):
        self.client.collection_events.update(
            {
                5001: secsgem.gem.CollectionEvent(5001, "TEST_RCMD complete", []),
            }
        )
        self.client.remote_commands.update(
            {
                "TEST_RCMD": secsgem.gem.RemoteCommand("TEST_RCMD", "test rcmd", ["TEST_PARAMETER"], 5001),
            }
        )

    def sendCEDefineReport(self, dataid=100, rptid=1000, vid=None, empty_data=False):
        if vid is None:
            vid = [30]
        if not empty_data:
            data = {"DATAID": dataid, "DATA": [{"RPTID": rptid, "VID": vid}]}
        else:
            data = {"DATAID": dataid, "DATA": []}

        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(secsgem.secs.functions.SecsS02F33(data), system_id)
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 34

        return self.client.streams_functions.decode(packet)

    def sendCELinkReport(self, dataid=100, ceid=50, rptid=None, empty_data=False):
        if rptid is None:
            rptid = [1000]
        if not empty_data:
            data = {"DATAID": dataid, "DATA": [{"CEID": ceid, "RPTID": rptid}]}
        else:
            data = {"DATAID": dataid, "DATA": []}

        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(secsgem.secs.functions.SecsS02F35(data), system_id)
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 36

        return self.client.streams_functions.decode(packet)

    def sendCEEnableReport(self, enable=True, ceid=None):
        if ceid is None:
            ceid = [50]
        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS02F37({"CEED": enable, "CEID": ceid}), system_id
            )
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 38

        return self.client.streams_functions.decode(packet)

    def sendAlarmEnable(self, enable=True, alid=25):
        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS05F03(
                    {
                        "ALED": secsgem.secs.data_items.ALED.ENABLE if enable else secsgem.secs.data_items.ALED.DISABLE,
                        "ALID": alid,
                    }
                ),
                system_id,
            )
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 5
        assert packet.header.function == 4

        return self.client.streams_functions.decode(packet)

    def sendCERequestReport(self, ceid=50):
        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(secsgem.secs.functions.SecsS06F15(ceid), system_id)
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 6
        assert packet.header.function == 16

        return self.client.streams_functions.decode(packet)

    def testCollectionEventRegisterReport(self):
        self.setupTestDataValues()
        self.establishCommunication()

        oldlen = len(self.client.registered_reports)

        function = self.sendCEDefineReport()

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_reports) == oldlen + 1

    def testCollectionEventClearReports(self):
        self.setupTestDataValues()
        self.establishCommunication()

        function = self.sendCEDefineReport()

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_reports) > 0

        function = self.sendCEDefineReport(empty_data=True)

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_reports) == 0

    def testCollectionEventRemoveReport(self):
        self.setupTestDataValues()
        self.establishCommunication()

        oldlen = len(self.client.registered_reports)

        function = self.sendCEDefineReport()

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_reports) > 0

        function = self.sendCEDefineReport(vid=[])

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_reports) == oldlen

    def testCollectionEventRemoveReportWithLinkedCE(self):
        self.setupTestDataValues()
        self.setupTestCollectionEvents()
        self.establishCommunication()

        oldlenRPT = len(self.client.registered_reports)
        oldlenCE = len(self.client.registered_collection_events)

        function = self.sendCEDefineReport()

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_reports) == oldlenRPT + 1

        function = self.sendCELinkReport()

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_collection_events) == oldlenCE + 1

        function = self.sendCEDefineReport(vid=[])

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_reports) == oldlenRPT
        assert len(self.client.registered_collection_events) == oldlenCE

    def testCollectionEventRegisterReportWithInvalidVID(self):
        self.establishCommunication()

        function = self.sendCEDefineReport(vid=[9876])

        assert function.get() is not None
        assert function.get() == 4

    def testCollectionEventDuplicateRegisterReport(self):
        self.setupTestDataValues()
        self.establishCommunication()

        function = self.sendCEDefineReport()

        assert function.get() is not None
        assert function.get() == 0

        function = self.sendCEDefineReport()

        assert function.get() is not None
        assert function.get() == 3

    def testCollectionEventLinkReport(self):
        self.setupTestDataValues()
        self.setupTestCollectionEvents()
        self.establishCommunication()

        oldlenRPT = len(self.client.registered_reports)
        oldlenCE = len(self.client.registered_collection_events)

        function = self.sendCEDefineReport()

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_reports) == oldlenRPT + 1

        function = self.sendCELinkReport()

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_collection_events) == oldlenCE + 1

    def testCollectionEventLinkReportUnknownCEID(self):
        self.setupTestDataValues()
        self.establishCommunication()

        oldlenRPT = len(self.client.registered_reports)
        len(self.client.registered_collection_events)

        function = self.sendCEDefineReport()

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_reports) == oldlenRPT + 1

        function = self.sendCELinkReport()

        assert function.get() is not None
        assert function.get() == 4

    def testCollectionEventDuplicateLinkReport(self):
        self.setupTestDataValues()
        self.setupTestCollectionEvents()
        self.establishCommunication()

        oldlenRPT = len(self.client.registered_reports)
        oldlenCE = len(self.client.registered_collection_events)

        function = self.sendCEDefineReport()

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_reports) == oldlenRPT + 1

        function = self.sendCELinkReport()

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_collection_events) == oldlenCE + 1

        function = self.sendCELinkReport()

        assert function.get() is not None
        assert function.get() == 3

        assert len(self.client.registered_collection_events) == oldlenCE + 1

    def testCollectionEventLinkReportUnknown(self):
        self.setupTestDataValues()
        self.setupTestCollectionEvents()
        self.establishCommunication()

        oldlenCE = len(self.client.registered_collection_events)

        function = self.sendCELinkReport()

        assert function.get() is not None
        assert function.get() == 5

        assert len(self.client.registered_collection_events) == oldlenCE

    def testCollectionEventUnlinkReport(self):
        self.setupTestDataValues()
        self.setupTestCollectionEvents()
        self.establishCommunication()

        oldlenRPT = len(self.client.registered_reports)
        oldlenCE = len(self.client.registered_collection_events)

        function = self.sendCEDefineReport()

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_reports) == oldlenRPT + 1

        function = self.sendCELinkReport()

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_collection_events) == oldlenCE + 1

        function = self.sendCELinkReport(rptid=[])

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_collection_events) == oldlenCE

    def testCollectionEventLinkTwoReports(self):
        self.setupTestDataValues()
        self.setupTestCollectionEvents()
        self.establishCommunication()

        oldlenRPT = len(self.client.registered_reports)
        oldlenCE = len(self.client.registered_collection_events)

        function = self.sendCEDefineReport()

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_reports) == oldlenRPT + 1

        function = self.sendCEDefineReport(rptid=1001)

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_reports) == oldlenRPT + 2

        function = self.sendCELinkReport()

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_collection_events) == oldlenCE + 1

        function = self.sendCELinkReport(rptid=[1001])

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_collection_events) == oldlenCE + 1

    def testCollectionEventEnableReport(self):
        self.setupTestDataValues()
        self.setupTestCollectionEvents()
        self.establishCommunication()

        oldlenRPT = len(self.client.registered_reports)
        oldlenCE = len(self.client.registered_collection_events)

        function = self.sendCEDefineReport()

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_reports) == oldlenRPT + 1

        function = self.sendCELinkReport()

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_collection_events) == oldlenCE + 1

        function = self.sendCEEnableReport()

        assert function.get() is not None
        assert function.get() == 0

    def testCollectionEventEnableAllReports(self):
        self.setupTestDataValues()
        self.setupTestCollectionEvents()
        self.establishCommunication()

        oldlenRPT = len(self.client.registered_reports)
        oldlenCE = len(self.client.registered_collection_events)

        function = self.sendCEDefineReport()

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_reports) == oldlenRPT + 1

        function = self.sendCELinkReport()

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_collection_events) == oldlenCE + 1

        function = self.sendCEEnableReport(ceid=[])

        assert function.get() is not None
        assert function.get() == 0

    def testCollectionEventEnableUnlinkedReport(self):
        self.setupTestDataValues()
        self.setupTestCollectionEvents()
        self.establishCommunication()

        oldlenRPT = len(self.client.registered_reports)
        len(self.client.registered_collection_events)

        function = self.sendCEDefineReport()

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_reports) == oldlenRPT + 1

        function = self.sendCEEnableReport()

        assert function.get() is not None
        assert function.get() == 1

    def testCollectionEventRequestReport(self):
        self.setupTestDataValues()
        self.setupTestCollectionEvents()
        self.establishCommunication()

        oldlenRPT = len(self.client.registered_reports)
        oldlenCE = len(self.client.registered_collection_events)

        function = self.sendCEDefineReport()

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_reports) == oldlenRPT + 1

        function = self.sendCELinkReport()

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_collection_events) == oldlenCE + 1

        function = self.sendCEEnableReport()

        assert function.get() is not None
        assert function.get() == 0

        function = self.sendCERequestReport()

        assert function.get() is not None
        assert function.CEID.get() == 50
        assert function.RPT[0].RPTID.get() == 1000
        assert function.RPT[0].V[0].get() == 31337

    def testCollectionEventRequestReportCallbackSV(self):
        self.setupTestDataValues(True)
        self.setupTestCollectionEvents()
        self.setupTestStatusVariables(True)
        self.establishCommunication()

        oldlenRPT = len(self.client.registered_reports)
        oldlenCE = len(self.client.registered_collection_events)

        function = self.sendCEDefineReport(vid=[30, 10])

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_reports) == oldlenRPT + 1

        function = self.sendCELinkReport()

        assert function.get() is not None
        assert function.get() == 0

        assert len(self.client.registered_collection_events) == oldlenCE + 1

        function = self.sendCEEnableReport()

        assert function.get() is not None
        assert function.get() == 0

        function = self.sendCERequestReport()

        assert function.get() is not None
        assert function.CEID.get() == 50
        assert function.RPT[0].RPTID.get() == 1000
        assert function.RPT[0].V[0].get() == 31337
        assert function.RPT[0].V[1].get() == 123

    def testCollectionEventTrigger(self):
        self.setupTestDataValues()
        self.setupTestCollectionEvents()
        self.establishCommunication()

        function = self.sendCEDefineReport()
        function = self.sendCELinkReport()
        function = self.sendCEEnableReport()

        clientCommandThread = threading.Thread(
            target=self.client.trigger_collection_events,
            args=([50],),
            name="TestGemEquipmentHandlerPassiveControlState_testCollectionEventTrigger",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(stream=6)

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS06F12(0), packet.header.system
            )
        )

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 6
        assert packet.header.function == 11

        function = self.client.streams_functions.decode(packet)

        assert function.get() is not None
        assert function.CEID.get() == 50
        assert function.RPT[0].RPTID.get() == 1000
        assert function.RPT[0].V[0].get() == 31337

    def setupTestEquipmentConstants(self, use_callback=False):
        self.client.equipment_constants.update(
            {
                20: secsgem.gem.EquipmentConstant(
                    20, "sample1, numeric ECID, I4", 0, 500, 50, "degrees", secsgem.secs.variables.I4, use_callback
                ),
                "EC2": secsgem.gem.EquipmentConstant(
                    "EC2",
                    "sample2, text ECID, String",
                    None,
                    None,
                    "",
                    "chars",
                    secsgem.secs.variables.String,
                    use_callback,
                ),
            }
        )

        self.client.equipment_constants[20].value = 321
        self.client.equipment_constants["EC2"].value = "sample ec"

    def sendECNamelistRequest(self, ecid=None):
        if ecid is None:
            ecid = []
        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(secsgem.secs.functions.SecsS02F29(ecid), system_id)
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 30

        return self.client.streams_functions.decode(packet)

    def sendECRequest(self, ecid=None):
        if ecid is None:
            ecid = []
        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(secsgem.secs.functions.SecsS02F13(ecid), system_id)
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 14

        return self.client.streams_functions.decode(packet)

    def sendECUpdate(self, data):
        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(secsgem.secs.functions.SecsS02F15(data), system_id)
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 16

        return self.client.streams_functions.decode(packet)

    def testEquipmentConstantNameListAll(self):
        self.setupTestEquipmentConstants()
        self.establishCommunication()

        function = self.sendECNamelistRequest()

        EC2 = next((x for x in function if x[0].get() == "EC2"), None)

        assert EC2 is not None
        assert EC2[1].get() == "sample2, text ECID, String"
        assert EC2[2].get() == ""
        assert EC2[3].get() == ""
        assert EC2[4].get() == ""
        assert EC2[5].get() == "chars"

        EC20 = next((x for x in function if x[0].get() == 20), None)

        assert EC20 is not None
        assert EC20[1].get() == "sample1, numeric ECID, I4"
        assert EC20[2].get() == 0
        assert EC20[3].get() == 500
        assert EC20[4].get() == 50
        assert EC20[5].get() == "degrees"

    def testEquipmentConstantNameListLimited(self):
        self.setupTestEquipmentConstants()
        self.establishCommunication()

        function = self.sendECNamelistRequest(["EC2", 20])

        EC2 = function[0]

        assert EC2 is not None
        assert EC2[0].get() == "EC2"
        assert EC2[1].get() == "sample2, text ECID, String"
        assert EC2[2].get() == ""
        assert EC2[3].get() == ""
        assert EC2[4].get() == ""
        assert EC2[5].get() == "chars"

        EC20 = function[1]

        assert EC20 is not None
        assert EC20[0].get() == 20
        assert EC20[1].get() == "sample1, numeric ECID, I4"
        assert EC20[2].get() == 0
        assert EC20[3].get() == 500
        assert EC20[4].get() == 50
        assert EC20[5].get() == "degrees"

    def testEquipmentConstantNameListInvalid(self):
        self.setupTestEquipmentConstants()
        self.establishCommunication()

        function = self.sendECNamelistRequest(["asdfg"])

        EC2 = function[0]

        assert EC2 is not None
        assert EC2[0].get() == "asdfg"
        assert EC2[1].get() == ""
        assert EC2[2].get() == ""
        assert EC2[3].get() == ""
        assert EC2[4].get() == ""
        assert EC2[5].get() == ""

    def testEquipmentConstantGetAll(self):
        self.setupTestEquipmentConstants()
        self.establishCommunication()

        function = self.sendECRequest()

        EC20 = next((x for x in function if x.get() == 321), None)
        assert EC20 is not None

        EC2 = next((x for x in function if x.get() == "sample ec"), None)
        assert EC2 is not None

    def testEquipmentConstantGetLimited(self):
        self.setupTestEquipmentConstants()
        self.establishCommunication()

        function = self.sendECRequest([20, "EC2"])

        EC20 = function[0]
        assert EC20 is not None
        assert EC20.get() == 321

        EC2 = function[1]
        assert EC2 is not None
        assert EC2.get() == "sample ec"

    def testEquipmentConstantGetCallback(self):
        self.setupTestEquipmentConstants(True)
        self.establishCommunication()

        function = self.sendECRequest([20, "EC2"])

        EC20 = function[0]
        assert EC20 is not None
        assert EC20.get() == 321

        EC2 = function[1]
        assert EC2 is not None
        assert EC2.get() == "sample ec"

    def testEquipmentConstantGetInvalid(self):
        self.setupTestEquipmentConstants()
        self.establishCommunication()

        function = self.sendECRequest(["asdfg"])

        EC20 = function[0]
        assert EC20 is not None
        assert EC20.get() == []

    def testEquipmentConstantSetLimited(self):
        self.setupTestEquipmentConstants()
        self.establishCommunication()

        function = self.sendECUpdate(
            [{"ECID": 20, "ECV": secsgem.secs.variables.I4(123)}, {"ECID": "EC2", "ECV": "ce elpmas"}]
        )

        assert function.get() == 0

        assert self.client.equipment_constants[20].value == 123
        assert self.client.equipment_constants["EC2"].value == "ce elpmas"

    def testEquipmentConstantSetTooLow(self):
        self.setupTestEquipmentConstants()
        self.establishCommunication()

        function = self.sendECUpdate([{"ECID": 20, "ECV": secsgem.secs.variables.I4(-1)}])

        assert function.get() == 3

        assert self.client.equipment_constants[20].value == 321

    def testEquipmentConstantSetTooHigh(self):
        self.setupTestEquipmentConstants()
        self.establishCommunication()

        function = self.sendECUpdate([{"ECID": 20, "ECV": secsgem.secs.variables.I4(501)}])

        assert function.get() == 3

        assert self.client.equipment_constants[20].value == 321

    def testEquipmentConstantSetCallback(self):
        self.setupTestEquipmentConstants(True)
        self.establishCommunication()

        function = self.sendECUpdate(
            [{"ECID": 20, "ECV": secsgem.secs.variables.I4(123)}, {"ECID": "EC2", "ECV": "ce elpmas"}]
        )

        assert function.get() == 0

        assert self.client.equipment_constants[20].value == 123
        assert self.client.equipment_constants["EC2"].value == "ce elpmas"

    def testEquipmentConstantSetInvalid(self):
        self.setupTestEquipmentConstants()
        self.establishCommunication()

        function = self.sendECUpdate([{"ECID": "asdfg", "ECV": "ce elpmas"}])

        assert function.get() == 1

    def testEquipmentConstantPredefinedEstablishCommunicationTimeout(self):
        self.client.equipment_constants[
            secsgem.gem.EquipmentConstantId.ESTABLISH_COMMUNICATIONS_TIMEOUT.value
        ].value = 10

        self.establishCommunication()

        function = self.sendECRequest([secsgem.gem.EquipmentConstantId.ESTABLISH_COMMUNICATIONS_TIMEOUT.value])

        EC = function[0]
        assert EC is not None
        assert EC.get() == 10

        function = self.sendECUpdate(
            [
                {
                    "ECID": secsgem.gem.EquipmentConstantId.ESTABLISH_COMMUNICATIONS_TIMEOUT.value,
                    "ECV": secsgem.secs.variables.I4(20),
                }
            ]
        )

        assert function.get() == 0

        assert (
            self.client.equipment_constants[
                secsgem.gem.EquipmentConstantId.ESTABLISH_COMMUNICATIONS_TIMEOUT.value
            ].value
            == 20
        )

    def testEquipmentConstantPredefinedTimeFormat(self):
        self.client.equipment_constants[secsgem.gem.EquipmentConstantId.TIME_FORMAT.value].value = 1

        self.establishCommunication()

        function = self.sendECRequest([secsgem.gem.EquipmentConstantId.TIME_FORMAT.value])

        EC = function[0]
        assert EC is not None
        assert EC.get() == 1

        function = self.sendECUpdate(
            [{"ECID": secsgem.gem.EquipmentConstantId.TIME_FORMAT.value, "ECV": secsgem.secs.variables.I4(0)}]
        )

        assert function.get() == 0

        assert self.client.equipment_constants[secsgem.gem.EquipmentConstantId.TIME_FORMAT.value].value == 0

    def testAlarmEnable(self):
        self.setupTestAlarms()
        self.establishCommunication()

        assert not self.client.alarms[25].enabled

        function = self.sendAlarmEnable()

        assert function.get() == secsgem.secs.data_items.ACKC5.ACCEPTED
        assert self.client.alarms[25].enabled

    def testAlarmEnableUnknown(self):
        self.establishCommunication()

        function = self.sendAlarmEnable(alid=26)

        assert function.get() == secsgem.secs.data_items.ACKC5.ERROR

    def testAlarmDisable(self):
        self.setupTestAlarms()
        self.establishCommunication()

        assert not self.client.alarms[25].enabled

        function = self.sendAlarmEnable()

        assert function.get() == secsgem.secs.data_items.ACKC5.ACCEPTED
        assert self.client.alarms[25].enabled

        function = self.sendAlarmEnable(enable=False)

        assert function.get() == secsgem.secs.data_items.ACKC5.ACCEPTED
        assert not self.client.alarms[25].enabled

    def testAlarmDisableUnknown(self):
        self.establishCommunication()

        function = self.sendAlarmEnable(enable=False, alid=26)

        assert function.get() == secsgem.secs.data_items.ACKC5.ERROR

    def testAlarmTriggerOn(self):
        self.setupTestAlarms()
        self.establishCommunication()

        function = self.sendAlarmEnable()

        assert not self.client.alarms[25].set

        clientCommandThread = threading.Thread(
            target=self.client.set_alarm,
            args=(25,),
            name="TestGemEquipmentHandlerPassiveControlState_testAlarmTriggerOn",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=1)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 5
        assert packet.header.function == 1

        function = self.client.streams_functions.decode(packet)

        assert (
            function.ALCD.get()
            == secsgem.secs.data_items.ALCD.PERSONAL_SAFETY
            | secsgem.secs.data_items.ALCD.EQUIPMENT_SAFETY
            | secsgem.secs.data_items.ALCD.ALARM_SET
        )
        assert function.ALID.get() == 25
        assert function.ALTX.get() == "test text"

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS05F02(secsgem.secs.data_items.ACKC5.ACCEPTED), packet.header.system
            )
        )

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        assert self.client.alarms[25].set

    def testAlarmTriggerOff(self):
        self.setupTestAlarms()
        self.establishCommunication()

        function = self.sendAlarmEnable()

        assert not self.client.alarms[25].set

        clientCommandThread = threading.Thread(
            target=self.client.set_alarm,
            args=(25,),
            name="TestGemEquipmentHandlerPassiveControlState_testAlarmTriggerOff",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=1)

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS05F02(secsgem.secs.data_items.ACKC5.ACCEPTED), packet.header.system
            )
        )

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        assert self.client.alarms[25].set

        clientCommandThread = threading.Thread(
            target=self.client.clear_alarm,
            args=(25,),
            name="TestGemEquipmentHandlerPassiveControlState_testAlarmTriggerOff",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=1)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 5
        assert packet.header.function == 1

        function = self.client.streams_functions.decode(packet)

        assert (
            function.ALCD.get()
            == secsgem.secs.data_items.ALCD.PERSONAL_SAFETY | secsgem.secs.data_items.ALCD.EQUIPMENT_SAFETY
        )
        assert function.ALID.get() == 25
        assert function.ALTX.get() == "test text"

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS05F02(secsgem.secs.data_items.ACKC5.ACCEPTED), packet.header.system
            )
        )

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        assert not self.client.alarms[25].set

    def testAlarmTriggerOnDisabled(self):
        self.setupTestAlarms()
        self.establishCommunication()

        assert not self.client.alarms[25].set

        clientCommandThread = threading.Thread(
            target=self.client.set_alarm,
            args=(25,),
            name="TestGemEquipmentHandlerPassiveControlState_testAlarmTriggerOnDisabled",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        assert self.client.alarms[25].set

    def testAlarmTriggerOffDisabled(self):
        self.setupTestAlarms()
        self.establishCommunication()

        assert not self.client.alarms[25].set

        clientCommandThread = threading.Thread(
            target=self.client.set_alarm,
            args=(25,),
            name="TestGemEquipmentHandlerPassiveControlState_testAlarmTriggerOffDisabled",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        assert self.client.alarms[25].set

        clientCommandThread = threading.Thread(
            target=self.client.clear_alarm,
            args=(25,),
            name="TestGemEquipmentHandlerPassiveControlState_testAlarmTriggerOffDisabled",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        assert not self.client.alarms[25].set

    def testAlarmTriggerAlreadyOn(self):
        self.setupTestAlarms()
        self.establishCommunication()

        self.sendAlarmEnable()

        assert not self.client.alarms[25].set

        clientCommandThread = threading.Thread(
            target=self.client.set_alarm,
            args=(25,),
            name="TestGemEquipmentHandlerPassiveControlState_testAlarmTriggerAlreadyOn",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=1)

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS05F02(secsgem.secs.data_items.ACKC5.ACCEPTED), packet.header.system
            )
        )

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        assert self.client.alarms[25].set

        clientCommandThread = threading.Thread(
            target=self.client.set_alarm,
            args=(25,),
            name="TestGemEquipmentHandlerPassiveControlState_testAlarmTriggerAlreadyOn",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        assert self.client.alarms[25].set

    def testAlarmTriggerAlreadyOff(self):
        self.setupTestAlarms()
        self.establishCommunication()

        self.sendAlarmEnable()

        assert not self.client.alarms[25].set

        clientCommandThread = threading.Thread(
            target=self.client.clear_alarm,
            args=(25,),
            name="TestGemEquipmentHandlerPassiveControlState_testAlarmTriggerAlreadyOff",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        assert not self.client.alarms[25].set

    def testAlarmTriggerOnCollectionEventWithEnabledAlarm(self):
        self.setupTestAlarms()
        self.establishCommunication()

        function = self.sendCEDefineReport(vid=[secsgem.gem.StatusVariableId.CLOCK.value])
        assert function.get() == 0
        function = self.sendCELinkReport(ceid=100025)
        assert function.get() == 0
        function = self.sendCEEnableReport(ceid=[100025])
        assert function.get() == 0

        function = self.sendAlarmEnable()

        assert not self.client.alarms[25].set

        clientCommandThread = threading.Thread(
            target=self.client.set_alarm,
            args=(25,),
            name="TestGemEquipmentHandlerPassiveControlState_testAlarmTriggerOnCollectionEvent",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=1)

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS05F02(secsgem.secs.data_items.ACKC5.ACCEPTED), packet.header.system
            )
        )

        packet = self.settings.protocol.expect_message(stream=6)

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS06F12(0), packet.header.system
            )
        )

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        assert self.client.alarms[25].set

    def testAlarmTriggerOnCollectionEvent(self):
        self.setupTestAlarms()
        self.establishCommunication()

        function = self.sendCEDefineReport(vid=[secsgem.gem.StatusVariableId.CLOCK.value])
        assert function.get() == 0
        function = self.sendCELinkReport(ceid=100025)
        assert function.get() == 0
        function = self.sendCEEnableReport(ceid=[100025])
        assert function.get() == 0

        assert not self.client.alarms[25].set

        clientCommandThread = threading.Thread(
            target=self.client.set_alarm,
            args=(25,),
            name="TestGemEquipmentHandlerPassiveControlState_testAlarmTriggerOnCollectionEvent",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(stream=6)

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS06F12(0), packet.header.system
            )
        )

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        assert self.client.alarms[25].set

    def testAlarmTriggerOffCollectionEvent(self):
        self.setupTestAlarms()
        self.establishCommunication()

        function = self.sendCEDefineReport(vid=[secsgem.gem.StatusVariableId.CLOCK.value])
        assert function.get() == 0
        function = self.sendCELinkReport(ceid=200025)
        assert function.get() == 0
        function = self.sendCEEnableReport(ceid=[200025])
        assert function.get() == 0

        function = self.sendAlarmEnable()

        assert not self.client.alarms[25].set

        clientCommandThread = threading.Thread(
            target=self.client.set_alarm,
            args=(25,),
            name="TestGemEquipmentHandlerPassiveControlState_testAlarmTriggerOffCollectionEvent",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=1)

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS05F02(secsgem.secs.data_items.ACKC5.ACCEPTED), packet.header.system
            )
        )

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        assert self.client.alarms[25].set

        clientCommandThread = threading.Thread(
            target=self.client.clear_alarm,
            args=(25,),
            name="TestGemEquipmentHandlerPassiveControlState_testAlarmTriggerOffCollectionEvent",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=1)

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS05F02(secsgem.secs.data_items.ACKC5.ACCEPTED), packet.header.system
            )
        )

        packet = self.settings.protocol.expect_message(stream=6)

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS06F12(0), packet.header.system
            )
        )

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        assert not self.client.alarms[25].set

    def testAlarmDisabledTriggerOffCollectionEvent(self):
        self.setupTestAlarms()
        self.establishCommunication()

        function = self.sendCEDefineReport(vid=[secsgem.gem.StatusVariableId.CLOCK.value])
        assert function.get() == 0
        function = self.sendCELinkReport(ceid=200025)
        assert function.get() == 0
        function = self.sendCEEnableReport(ceid=[200025])
        assert function.get() == 0

        assert not self.client.alarms[25].set

        clientCommandThread = threading.Thread(
            target=self.client.set_alarm,
            args=(25,),
            name="TestGemEquipmentHandlerPassiveControlState_testAlarmDisabledTriggerOffCollectionEvent",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        assert self.client.alarms[25].set

        clientCommandThread = threading.Thread(
            target=self.client.clear_alarm,
            args=(25,),
            name="TestGemEquipmentHandlerPassiveControlState_testAlarmTriggerOn",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(stream=6)

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS06F12(0), packet.header.system
            )
        )

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        assert not self.client.alarms[25].set

    def testAlarmTriggerAlreadyOnCollectionEvent(self):
        self.setupTestAlarms()
        self.establishCommunication()

        function = self.sendAlarmEnable()

        assert not self.client.alarms[25].set

        clientCommandThread = threading.Thread(
            target=self.client.set_alarm,
            args=(25,),
            name="TestGemEquipmentHandlerPassiveControlState_testAlarmTriggerAlreadyOnCollectionEvent",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=1)

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS05F02(secsgem.secs.data_items.ACKC5.ACCEPTED), packet.header.system
            )
        )

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        assert self.client.alarms[25].set

        function = self.sendCEDefineReport(vid=[secsgem.gem.StatusVariableId.CLOCK.value])
        assert function.get() == 0
        function = self.sendCELinkReport(ceid=100025)
        assert function.get() == 0
        function = self.sendCEEnableReport(ceid=[100025])
        assert function.get() == 0

        clientCommandThread = threading.Thread(
            target=self.client.set_alarm,
            args=(25,),
            name="TestGemEquipmentHandlerPassiveControlState_testAlarmTriggerAlreadyOnCollectionEvent",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        assert self.client.alarms[25].set

    def testAlarmTriggerAlreadyOffCollectionEvent(self):
        self.setupTestAlarms()
        self.establishCommunication()

        function = self.sendAlarmEnable()

        assert not self.client.alarms[25].set

        function = self.sendCEDefineReport(vid=[secsgem.gem.StatusVariableId.CLOCK.value])
        assert function.get() == 0
        function = self.sendCELinkReport(ceid=100025)
        assert function.get() == 0
        function = self.sendCEEnableReport(ceid=[100025])
        assert function.get() == 0

        clientCommandThread = threading.Thread(
            target=self.client.clear_alarm,
            args=(25,),
            name="TestGemEquipmentHandlerPassiveControlState_testAlarmTriggerAlreadyOffCollectionEvent",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

        assert not self.client.alarms[25].set

    def testAlarmTriggerOnUnknown(self):
        self.setupTestAlarms()
        self.establishCommunication()

        self.sendAlarmEnable()

        with pytest.raises(ValueError):
            self.client.set_alarm(26)

    def testAlarmTriggerOffUnknown(self):
        self.setupTestAlarms()
        self.establishCommunication()

        self.sendAlarmEnable()

        with pytest.raises(ValueError):
            self.client.clear_alarm(26)

    def testAlarmListAll(self):
        self.setupTestAlarms()
        self.establishCommunication()

        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(secsgem.secs.functions.SecsS05F05(), system_id)
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 5
        assert packet.header.function == 6

        function = self.client.streams_functions.decode(packet)

        assert len(function) == 2

        AL25 = next((x for x in function if x[1].get() == 25), None)

        assert AL25 is not None
        assert (
            AL25[0].get()
            == secsgem.secs.data_items.ALCD.PERSONAL_SAFETY | secsgem.secs.data_items.ALCD.EQUIPMENT_SAFETY
        )
        assert AL25[2].get() == "test text"

        AL30 = next((x for x in function if x[1].get() == 30), None)

        assert AL30 is not None
        assert (
            AL30[0].get()
            == secsgem.secs.data_items.ALCD.PERSONAL_SAFETY | secsgem.secs.data_items.ALCD.EQUIPMENT_SAFETY
        )
        assert AL30[2].get() == "test text 2"

    def testAlarmListSingle(self):
        self.setupTestAlarms()
        self.establishCommunication()

        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(secsgem.secs.functions.SecsS05F05([25]), system_id)
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 5
        assert packet.header.function == 6

        function = self.client.streams_functions.decode(packet)

        assert len(function) == 1

        AL25 = function[0]

        assert AL25 is not None
        assert (
            AL25[0].get()
            == secsgem.secs.data_items.ALCD.PERSONAL_SAFETY | secsgem.secs.data_items.ALCD.EQUIPMENT_SAFETY
        )
        assert AL25[1].get() == 25
        assert AL25[2].get() == "test text"

    def testAlarmListEnabled(self):
        self.setupTestAlarms()
        self.establishCommunication()

        function = self.sendAlarmEnable()

        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(secsgem.secs.functions.SecsS05F07(), system_id)
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 5
        assert packet.header.function == 8

        function = self.client.streams_functions.decode(packet)

        assert len(function) == 1

        AL25 = function[0]

        assert AL25 is not None
        assert (
            AL25[0].get()
            == secsgem.secs.data_items.ALCD.PERSONAL_SAFETY | secsgem.secs.data_items.ALCD.EQUIPMENT_SAFETY
        )
        assert AL25[1].get() == 25
        assert AL25[2].get() == "test text"

    def testRemoteCommand(self):
        self.setupTestRemoteCommands()
        self.establishCommunication()

        function = self.sendCEDefineReport(vid=[secsgem.gem.StatusVariableId.CLOCK.value])
        assert function.get() == 0
        function = self.sendCELinkReport(ceid=5001)
        assert function.get() == 0
        function = self.sendCEEnableReport(ceid=[5001])
        assert function.get() == 0

        f = unittest.mock.Mock()

        self.client.callbacks.rcmd_TEST_RCMD = f

        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS02F41(
                    {"RCMD": "TEST_RCMD", "PARAMS": [{"CPNAME": "TEST_PARAMETER", "CPVAL": ""}]}
                ),
                system_id,
            )
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 42

        function = self.client.streams_functions.decode(packet)

        assert function is not None
        assert function.HCACK.get() == secsgem.secs.data_items.HCACK.ACK_FINISH_LATER

        packet = self.settings.protocol.expect_message(stream=6)

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS06F12(0), packet.header.system
            )
        )

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 6
        assert packet.header.function == 11

        function = self.client.streams_functions.decode(packet)

        assert function.get() is not None
        assert function.CEID.get() == 5001

        f.assert_called_once_with(TEST_PARAMETER="")

    def testRemoteCommandUnregisteredCommand(self):
        self.establishCommunication()

        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS02F41({"RCMD": "UNKNOWN_RCMD", "PARAMS": []}), system_id
            )
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 42

        function = self.client.streams_functions.decode(packet)

        assert function is not None
        assert function.HCACK.get() == secsgem.secs.data_items.HCACK.INVALID_COMMAND

    def testRemoteCommandUnregisteredCallback(self):
        self.setupTestRemoteCommands()
        self.establishCommunication()

        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS02F41({"RCMD": "TEST_RCMD", "PARAMS": []}), system_id
            )
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 42

        function = self.client.streams_functions.decode(packet)

        assert function is not None
        assert function.HCACK.get() == secsgem.secs.data_items.HCACK.INVALID_COMMAND

    def testRemoteCommandUnknownParameter(self):
        self.setupTestRemoteCommands()
        self.establishCommunication()

        f = unittest.mock.Mock()

        self.client.callbacks.rcmd_TEST_RCMD = f

        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS02F41(
                    {"RCMD": "TEST_RCMD", "PARAMS": [{"CPNAME": "INVALID_PARAMETER", "CPVAL": ""}]}
                ),
                system_id,
            )
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 42

        function = self.client.streams_functions.decode(packet)

        assert function is not None
        assert function.HCACK.get() == secsgem.secs.data_items.HCACK.PARAMETER_INVALID

        assert not f.called

    def testRemoteCommandSTART(self):
        self.setupTestRemoteCommands()
        self.establishCommunication()

        function = self.sendCEDefineReport(vid=[secsgem.gem.StatusVariableId.CLOCK.value])
        assert function.get() == 0
        function = self.sendCELinkReport(ceid=secsgem.gem.CollectionEventId.CMD_START_DONE.value)
        assert function.get() == 0
        function = self.sendCEEnableReport(ceid=[secsgem.gem.CollectionEventId.CMD_START_DONE.value])
        assert function.get() == 0

        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS02F41({"RCMD": "START", "PARAMS": []}), system_id
            )
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 42

        function = self.client.streams_functions.decode(packet)

        assert function is not None
        assert function.HCACK.get() == secsgem.secs.data_items.HCACK.ACK_FINISH_LATER

        packet = self.settings.protocol.expect_message(stream=6)

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS06F12(0), packet.header.system
            )
        )

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 6
        assert packet.header.function == 11

        function = self.client.streams_functions.decode(packet)

        assert function.get() is not None
        assert function.CEID.get() == secsgem.gem.CollectionEventId.CMD_START_DONE.value

    def testRemoteCommandSTOP(self):
        self.setupTestRemoteCommands()
        self.establishCommunication()

        function = self.sendCEDefineReport(vid=[secsgem.gem.StatusVariableId.CLOCK.value])
        assert function.get() == 0
        function = self.sendCELinkReport(ceid=secsgem.gem.CollectionEventId.CMD_STOP_DONE.value)
        assert function.get() == 0
        function = self.sendCEEnableReport(ceid=[secsgem.gem.CollectionEventId.CMD_STOP_DONE.value])
        assert function.get() == 0

        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS02F41({"RCMD": "STOP", "PARAMS": []}), system_id
            )
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 42

        function = self.client.streams_functions.decode(packet)

        assert function is not None
        assert function.HCACK.get() == secsgem.secs.data_items.HCACK.ACK_FINISH_LATER

        packet = self.settings.protocol.expect_message(stream=6)

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS06F12(0), packet.header.system
            )
        )

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 6
        assert packet.header.function == 11

        function = self.client.streams_functions.decode(packet)

        assert function.get() is not None
        assert function.CEID.get() == secsgem.gem.CollectionEventId.CMD_STOP_DONE.value
