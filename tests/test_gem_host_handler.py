#####################################################################
# test_gem_host_handler.py
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

import threading
import unittest
from collections import OrderedDict

from mock_protocol import MockProtocol
from mock_settings import MockSettings
from test_gem_handler import GemHandlerPassiveGroup

import secsgem.gem


class TestGemHostHandlerPassive(unittest.TestCase, GemHandlerPassiveGroup):
    __testClass = secsgem.gem.GemHostHandler

    def setUp(self):
        assert self.__testClass is not None

        self.settings = MockSettings(MockProtocol)

        self.client = self.__testClass(self.settings)

        self.client.enable()

    def tearDown(self):
        self.client.disable()

    def testClearCollectionEvents(self):
        self.establishCommunication()

        clientCommandThread = threading.Thread(
            target=self.client.clear_collection_events, name="TestGemHostHandlerPassive_testClearCollectionEvents"
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=37)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 37

        function = self.client.streams_functions.decode(packet)

        assert function["CEED"] == False
        assert function["CEID"].get() == []

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS02F38(secsgem.secs.data_items.ERACK.ACCEPTED), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        packet = self.settings.protocol.expect_message(function=33)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 33

        function = self.client.streams_functions.decode(packet)

        assert function["DATAID"] == 0
        assert function["DATA"].get() == []

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS02F34(secsgem.secs.data_items.DRACK.ACK), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def subscribeCollectionEvent(self, ceid, dvs, report_id):
        clientCommandThread = threading.Thread(
            target=self.client.subscribe_collection_event,
            args=(ceid, dvs, report_id),
            name="TestGemHostHandlerPassive_subscribeCollectionEvent",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=33)

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS02F34(secsgem.secs.data_items.DRACK.ACK), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        packet = self.settings.protocol.expect_message(function=35)

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS02F36(secsgem.secs.data_items.LRACK.ACK), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        packet = self.settings.protocol.expect_message(function=37)

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS02F38(secsgem.secs.data_items.ERACK.ACCEPTED), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testSubscribeCollectionEvent(self):
        self.establishCommunication()

        clientCommandThread = threading.Thread(
            target=self.client.subscribe_collection_event,
            args=(10, [20], 30),
            name="TestGemHostHandlerPassive_testSubscribeCollectionEvent",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=33)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 33

        function = self.client.streams_functions.decode(packet)

        assert function["DATAID"] == 0
        assert function["DATA"][0]["RPTID"] == 30
        assert function["DATA"][0]["VID"][0] == 20

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS02F34(secsgem.secs.data_items.DRACK.ACK), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        packet = self.settings.protocol.expect_message(function=35)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 35

        function = self.client.streams_functions.decode(packet)

        assert function["DATAID"] == 0
        assert function["DATA"][0]["CEID"] == 10
        assert function["DATA"][0]["RPTID"][0] == 30

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS02F36(secsgem.secs.data_items.LRACK.ACK), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        packet = self.settings.protocol.expect_message(function=37)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 37

        function = self.client.streams_functions.decode(packet)

        assert function["CEED"] == True
        assert function["CEID"][0] == 10

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS02F36(secsgem.secs.data_items.LRACK.ACK), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testSubscribeCollectionEventWithoutReportId(self):
        self.establishCommunication()

        clientCommandThread = threading.Thread(
            target=self.client.subscribe_collection_event,
            args=(10, [20]),
            name="TestGemHostHandlerPassive_testSubscribeCollectionEvent",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=33)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 33

        function = self.client.streams_functions.decode(packet)

        assert function["DATAID"] == 0
        assert function["DATA"][0]["VID"][0] == 20

        rptid = function["DATA"][0]["RPTID"]

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS02F34(secsgem.secs.data_items.DRACK.ACK), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        packet = self.settings.protocol.expect_message(function=35)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 35

        function = self.client.streams_functions.decode(packet)

        assert function["DATAID"] == 0
        assert function["DATA"][0]["CEID"] == 10
        assert function["DATA"][0]["RPTID"][0] == rptid

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS02F36(secsgem.secs.data_items.LRACK.ACK), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        packet = self.settings.protocol.expect_message(function=37)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 37

        function = self.client.streams_functions.decode(packet)

        assert function["CEED"] == True
        assert function["CEID"][0] == 10

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS02F36(secsgem.secs.data_items.LRACK.ACK), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def sendRemoteCommand(self, params):
        self.establishCommunication()

        clientCommandThread = threading.Thread(
            target=self.client.send_remote_command,
            args=("RCMD", params),
            name="TestGemHostHandlerPassive_testSendRemoteCommand",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=41)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 41

        function = self.client.streams_functions.decode(packet)

        assert function.RCMD.get() == "RCMD"
        assert function.PARAMS[0].CPNAME.get() == "PARAM1"
        assert function.PARAMS[0].CPVAL.get() == "PARAM1"
        assert function.PARAMS[1].CPNAME.get() == "PARAM2"
        assert function.PARAMS[1].CPVAL.get() == 2

        packetdata = {
            "HCACK": secsgem.secs.data_items.HCACK.INVALID_COMMAND,
            "PARAMS": [
                {"CPNAME": "PARAM1", "CPACK": secsgem.secs.data_items.CPACK.CPVAL_ILLEGAL_VALUE},
                {"CPNAME": "PARAM2", "CPACK": secsgem.secs.data_items.CPACK.CPVAL_ILLEGAL_FORMAT},
            ],
        }
        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS02F42(packetdata), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testSendRemoteCommandDict(self):
        self.sendRemoteCommand(OrderedDict((("PARAM1", "PARAM1"), ("PARAM2", 2))))

    def testSendRemoteCommandList(self):
        self.sendRemoteCommand([["PARAM1", "PARAM1"], ["PARAM2", 2]])

    def testDeleteProcessPrograms(self):
        self.establishCommunication()

        clientCommandThread = threading.Thread(
            target=self.client.delete_process_programs,
            args=(["PP1", "PP2"],),
            name="TestGemHostHandlerPassive_testDeleteProcessPrograms",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=17)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 7
        assert packet.header.function == 17

        function = self.client.streams_functions.decode(packet)

        assert function[0].get() == "PP1"
        assert function[1].get() == "PP2"

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS07F18(secsgem.secs.data_items.ACKC7.ACCEPTED), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testGetProcessProgramList(self):
        self.establishCommunication()

        clientCommandThread = threading.Thread(
            target=self.client.get_process_program_list, name="TestGemHostHandlerPassive_testGetProcessProgramList"
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=19)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 7
        assert packet.header.function == 19

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS07F20(["PP1", "PP2"]), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testGoOnline(self):
        self.establishCommunication()

        clientCommandThread = threading.Thread(
            target=self.client.go_online, name="TestGemHostHandlerPassive_testGoOnline"
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=17)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 1
        assert packet.header.function == 17

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS01F18(secsgem.secs.data_items.ONLACK.ACCEPTED), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testGoOffline(self):
        self.establishCommunication()

        clientCommandThread = threading.Thread(
            target=self.client.go_offline, name="TestGemHostHandlerPassive_testGoOffline"
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=15)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 1
        assert packet.header.function == 15

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS01F16(secsgem.secs.data_items.OFLACK.ACK), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testEnableAlarm(self):
        self.establishCommunication()

        clientCommandThread = threading.Thread(
            target=self.client.enable_alarm, args=(25,), name="TestGemHostHandlerPassive_testEnableAlarm"
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=3)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 5
        assert packet.header.function == 3

        function = self.client.streams_functions.decode(packet)

        assert function.ALED.get() == secsgem.secs.data_items.ALED.ENABLE
        assert function.ALID.get() == 25

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS05F04(secsgem.secs.data_items.ACKC5.ACCEPTED), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testDisableAlarm(self):
        self.establishCommunication()

        clientCommandThread = threading.Thread(
            target=self.client.disable_alarm, args=(25,), name="TestGemHostHandlerPassive_testDisableAlarm"
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=3)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 5
        assert packet.header.function == 3

        function = self.client.streams_functions.decode(packet)

        assert function.ALED.get() == secsgem.secs.data_items.ALED.DISABLE
        assert function.ALID.get() == 25

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS05F04(secsgem.secs.data_items.ACKC5.ACCEPTED), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testListAlarmsAll(self):
        self.establishCommunication()

        clientCommandThread = threading.Thread(
            target=self.client.list_alarms, name="TestGemHostHandlerPassive_testListAlarmsAll"
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=5)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 5
        assert packet.header.function == 5

        function = self.client.streams_functions.decode(packet)

        assert function.get() == []

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS05F06([]), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testListAlarmSingle(self):
        self.establishCommunication()

        clientCommandThread = threading.Thread(
            target=self.client.list_alarms, args=([25],), name="TestGemHostHandlerPassive_testListAlarmSingle"
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=5)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 5
        assert packet.header.function == 5

        function = self.client.streams_functions.decode(packet)

        assert function.get() == [25]

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS05F06([{"ALCD": 0, "ALID": 25, "ALTX": "sampleText"}]), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testListAlarmsEnabled(self):
        self.establishCommunication()

        clientCommandThread = threading.Thread(
            target=self.client.list_enabled_alarms, name="TestGemHostHandlerPassive_testListAlarmsEnabled"
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=7)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 5
        assert packet.header.function == 7

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS05F08([]), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testReceiveAlarm(self):
        self.establishCommunication()

        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS05F01(
                    {
                        "ALCD": secsgem.secs.data_items.ALCD.PERSONAL_SAFETY | secsgem.secs.data_items.ALCD.ALARM_SET,
                        "ALID": 100,
                        "ALTX": "text",
                    }
                ),
                system_id,
            )
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 5
        assert packet.header.function == 2

        function = self.client.streams_functions.decode(packet)

        assert function.get() == secsgem.secs.data_items.ACKC5.ACCEPTED

    def testReceiveTerminal(self):
        self.establishCommunication()

        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS10F01({"TID": 1, "TEXT": "HALLO"}), system_id
            )
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 10
        assert packet.header.function == 2

        function = self.client.streams_functions.decode(packet)

        assert function.get() == 0

    def testCollectionEventReceiving(self):
        self.establishCommunication()

        self.subscribeCollectionEvent(10, [20, 21], 30)

        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS06F11({"DATAID": 0, "CEID": 10, "RPT": [{"RPTID": 30, "V": ["1", 2]}]}),
                system_id,
            )
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 6
        assert packet.header.function == 12

        function = self.client.streams_functions.decode(packet)

        assert function.get() == 0
