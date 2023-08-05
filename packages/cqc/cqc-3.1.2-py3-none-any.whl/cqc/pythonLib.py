#
# Copyright (c) 2017, Stephanie Wehner and Axel Dahlberg
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. All advertising materials mentioning features or use of this software
#    must display the following acknowledgement:
#    This product includes software developed by Stephanie Wehner, QuTech.
# 4. Neither the name of the QuTech organization nor the
#    names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import math
import os
import sys
import time
import logging
import socket
import warnings
from typing import Union, Any, List
from anytree import NodeMixin

from cqc.cqcHeader import (
    Header,
    CQCCmdHeader,
    CQC_CMD_SEND,
    CQC_CMD_EPR,
    CQC_CMD_CNOT,
    CQC_CMD_CPHASE,
    CQC_CMD_ROT_X,
    CQC_CMD_ROT_Y,
    CQC_CMD_ROT_Z,
    CQC_TP_HELLO,
    CQC_TP_COMMAND,
    CQC_TP_FACTORY,
    CQC_TP_GET_TIME,
    CQC_CMD_I,
    CQC_CMD_X,
    CQC_CMD_Y,
    CQC_CMD_Z,
    CQC_CMD_T,
    CQC_CMD_H,
    CQC_CMD_K,
    CQC_CMD_NEW,
    CQC_CMD_MEASURE,
    CQC_CMD_MEASURE_INPLACE,
    CQC_CMD_RESET,
    CQC_CMD_RECV,
    CQC_CMD_EPR_RECV,
    CQC_CMD_ALLOCATE,
    CQC_CMD_RELEASE,
    CQCCommunicationHeader,
    CQCXtraQubitHeader,
    CQCRotationHeader,
    CQC_VERSION,
    CQCHeader,
    CQC_TP_DONE,
    CQC_ERR_UNSUPP,
    CQC_ERR_UNKNOWN,
    CQC_ERR_GENERAL,
    CQCSequenceHeader,
    CQCFactoryHeader,
    CQC_TP_INF_TIME,
    CQC_ERR_NOQUBIT,
    CQCMeasOutHeader,
    CQCTimeinfoHeader,
    CQC_TP_MEASOUT,
    CQC_ERR_TIMEOUT,
    CQC_TP_RECV,
    CQC_TP_EPR_OK,
    CQC_TP_NEW_OK,
    CQC_TP_EXPIRE,
    CQCLogicalOperator,
    CQCIfHeader,
    CQCTypeHeader,
    CQCType,
    CQCAssignHeader
)
from cqc.entInfoHeader import EntInfoHeader
from cqc.hostConfig import cqc_node_id_from_addrinfo

try:
    import simulaqron
    from simulaqron.general.hostConfig import socketsConfig
    from simulaqron.settings import simulaqron_settings
    _simulaqron_version = simulaqron.__version__
    _simulaqron_major = int(_simulaqron_version.split('.')[0])
except ImportError:
    _simulaqron_major = -1


def shouldReturn(command):
    return command in {
        CQC_CMD_NEW,
        CQC_CMD_MEASURE,
        CQC_CMD_MEASURE_INPLACE,
        CQC_CMD_RECV,
        CQC_CMD_EPR_RECV,
        CQC_CMD_EPR,
    }


def hasXtraHeader(command):
    return command in {
        CQC_CMD_CNOT,
        CQC_CMD_SEND,
        CQC_CMD_EPR,
        CQC_CMD_ROT_X,
        CQC_CMD_ROT_Y,
        CQC_CMD_ROT_Z,
        CQC_CMD_CPHASE,
    }


def get_remote_from_directory_or_address(cqcNet, name, remote_socket):
    if remote_socket is None:
        try:
            # Get receiving host
            hostDict = cqcNet.hostDict
        except AttributeError:
            raise ValueError(
                "If a CQCConnections is initialized without specifying a cqcFile you need to also provide a"
                "socket address for the remote node here."
            )
        if name in hostDict:
            recvHost = hostDict[name]
            remote_ip = recvHost.ip
            remote_port = recvHost.port
        else:
            raise ValueError("Host name '{}' is not in the cqc network".format(name))
    else:
        try:
            remote_host, remote_port = remote_socket
            if not isinstance(remote_host, str):
                raise TypeError()
            if not isinstance(remote_port, int):
                raise TypeError()
        except Exception:
            raise TypeError("When specifying the remote socket address, this should be a tuple (str,int).")

            # Pack the IP
        addrs = socket.getaddrinfo(remote_host, remote_port, proto=socket.IPPROTO_TCP, family=socket.AF_INET)
        addr = addrs[0]
        remote_ip = cqc_node_id_from_addrinfo(addr)
        remote_port = addr[4][1]
    return remote_ip, remote_port


# Deprecated. Do not use this method
def createXtraHeader(command, values):
    warnings.warn("Method 'createXtraHeader' is deprecated.", DeprecationWarning)

    if command == CQC_CMD_SEND or command == CQC_CMD_EPR:
        header = CQCCommunicationHeader()
        header.setVals(remote_app_id=values[0], remote_node=values[1], remote_port=values[2])
    elif command == CQC_CMD_CNOT or command == CQC_CMD_CPHASE:
        header = CQCXtraQubitHeader()
        xtra_qubit_id = values._qID
        if xtra_qubit_id is None:
            raise QubitNotActiveError("Qubit in extra header is not active")
        header.setVals(xtra_qubit_id)
    elif command == CQC_CMD_ROT_Z or command == CQC_CMD_ROT_Y or command == CQC_CMD_ROT_X:
        header = CQCRotationHeader()
        header.setVals(values)
    else:
        header = None
    return header


class CQCConnection:
    _appIDs = {}

    def __init__(self, name, socket_address=None, appID=None, pend_messages=False,
                 retry_connection=True, conn_retry_time=0.1, log_level=None, backend=None,
                 use_classical_communication=True, network_name=None):
        """
        Initialize a connection to the cqc server.

        Since version 3.0.0: If socket_address is None or use_classical_communication is True, the CQC connection
        needs some way of finding the correct socket addresses. If backend is None or "simulaqron" the connection
        will try to make use of the network config file setup in simulaqron. If simulaqron is not installed

        - **Arguments**
            :param name:        Name of the host.
            :param socket_address: tuple (str, int) of ip and port number.
            :param appID:        Application ID. If set to None, defaults to a nonused ID.
            :param pend_messages: True if you want to wait with sending messages to the back end.
                    Use flush() to send all pending messages in one go as a sequence to the server
            :param retry_connection: bool
                Whether to retry a failed connection or not
            :param conn_retry_time: float
                How many seconds to wait between each connection retry
            :param log_level: int or None
                The log-level, for example logging.DEBUG (default: logging.WARNING)
            :param backend: None or str
                If socket_address is None or use_classical_communication is True, If None or "simulaqron" is used
                the cqc library tries to use the network config file setup in simulaqron if network_config_file is None.
                If network_config_file is None and simulaqron is not installed a ValueError is raised.
            :param use_classical_communication: bool
                Whether to use the built-in classical communication or not.
            :param network_name: None or str
                Used if simulaqron is used to load socket addresses for the backend
        """
        self._setup_logging(log_level)

        # This flag is used to check if CQCConnection is opened using a 'with' statement.
        # Otherwise an deprecation warning is printed when instantiating qubits.
        self._opened_with_with = False

        # Host name
        self.name = name

        # Connection retry time
        self._conn_retry_time = conn_retry_time

        if name not in self._appIDs:
            self._appIDs[name] = []

            # Which appID
        if appID is None:
            if len(self._appIDs[name]) == 0:
                self._appID = 0
            else:
                for i in range(min(self._appIDs[name]) + 1, max(self._appIDs[name])):
                    if i not in self._appIDs[name]:
                        self._appID = i
                        break
                else:
                    self._appID = max(self._appIDs[name]) + 1
            self._appIDs[name].append(self._appID)
        else:
            if appID in self._appIDs:
                raise ValueError("appID={} is already in use".format(appID))
            self._appID = appID
            self._appIDs[name].append(self._appID)

        # Buffer received data
        self.buf = None

        # ClassicalServer
        self._classicalServer = None

        # Classical connections in the application network
        self._classicalConn = {}

        if socket_address is None or use_classical_communication:
            if backend is None or backend == "simulaqron":
                if _simulaqron_major < 3:
                    raise ValueError("If (socket_address is None or use_classical_communication is True)"
                                     "and (backend is None or 'simulaqron'\n"
                                     "you need simulaqron>=3.0.0 installed.")
                else:
                    network_config_file = simulaqron_settings.network_config_file
                    self._cqcNet = socketsConfig(network_config_file, network_name=network_name, config_type="cqc")
                    if use_classical_communication:
                        self._appNet = socketsConfig(network_config_file, network_name=network_name, config_type="app")
                    else:
                        self._appNet = None
            else:
                raise ValueError("Unknown backend")

            # Host data
            if self.name in self._cqcNet.hostDict:
                myHost = self._cqcNet.hostDict[self.name]
            else:
                raise ValueError("Host name '{}' is not in the cqc network".format(name))

                # Get IP and port number
            addr = myHost.addr
        if socket_address is not None:
            try:
                hostname, port = socket_address
                if not isinstance(hostname, str):
                    raise TypeError()
                if not isinstance(port, int):
                    raise TypeError()
                addrs = socket.getaddrinfo(hostname, port, proto=socket.IPPROTO_TCP, family=socket.AF_INET)
                addr = addrs[0]

            except Exception:
                raise TypeError("When specifying the socket address, this should be a tuple (str,int).")

        # All qubits active for this connection
        self.active_qubits = []

        # List of pended header objects waiting to be sent to the backend
        self._pending_headers = []  # ONLY cqc.cqcHeader.Header objects should be in this list

        # Bool that indicates whether we are in a factory and thus should pend commands
        self.pend_messages = pend_messages

        # Bool that indicates wheter we are in a CQCType.MIX
        self._inside_cqc_mix = False

        # Variable of type NodeMixin. This variable is used in CQCMix types to create a
        # scoping mechanism.
        self.current_scope = None

        self._s = None
        while True:
            try:
                logging.debug("App {} : Trying to connect to CQC server".format(self.name))

                self._s = socket.socket(addr[0], addr[1], addr[2])
                self._s.connect(addr[4])
                break
            except ConnectionRefusedError as err:
                logging.debug("App {} : Could not connect to  CQC server, trying again...".format(self.name))
                time.sleep(self._conn_retry_time)
                self._s.close()
                if not retry_connection:
                    self.close(release_qubits=False)
                    raise err
            except Exception as err:
                logging.warning("App {} : Critical error when connection to CQC server: {}".format(self.name, err))
                self._s.close()
                raise err

    def _pend_header(self, header: Header) -> None:
        self._pending_headers.append(header)

    def __enter__(self):
        # This flag is used to check if CQCConnection is opened using a 'with' statement.
        # Otherwise an deprecation warning is printed when instantiating qubits.
        self._opened_with_with = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # All qubits should now be released
        self.close(release_qubits=True)

    def __str__(self):
        return "Socket to cqc server '{}'".format(self.name)

    @staticmethod
    def _setup_logging(level):
        """
        Sets up the logging to the specified level (default logging.WARNING)
        :param level: int or None
            For example logging.DEBUG
        :return: None
        """
        if level is None:
            logging.basicConfig(format="%(asctime)s:%(levelname)s:%(message)s", level=logging.WARNING)
        else:
            logging.basicConfig(format="%(asctime)s:%(levelname)s:%(message)s", level=level)

    def get_appID(self):
        """
        Returns the application ID.
        """
        return self._appID

    def close(self, release_qubits=True):
        """Handle closing actions.

        Flushes remaining headers, releases all qubits, closes the 
        connections, and removes the app ID from the used app IDs.
        """

        # Flush all remaining commands
        if self._pending_headers:
            self.flush()

        if release_qubits:
            self.release_all_qubits()
        self._s.close()
        self._pop_app_id()

        self.closeClassicalServer()

        for name in list(self._classicalConn):
            self.closeClassicalChannel(name)

    def _pop_app_id(self):
        """
        Removes the used appID from the list.
        """
        try:
            self._appIDs[self.name].remove(self._appID)
        except ValueError:
            pass  # Already removed

    def startClassicalServer(self):
        """
        Sets up a server for the application communication, if not already set up.
        """
        if self._appNet is None:
            raise ValueError(
                "Since use_classical_communication was set to False upon init, the built-in classical communication"
                "cannot be used."
            )

        if not self._classicalServer:
            logging.debug("App {}: Starting classical server".format(self.name))
            # Get host data
            myHost = self._appNet.hostDict[self.name]
            hostaddr = myHost.addr

            # Setup server
            s = socket.socket(hostaddr[0], hostaddr[1], hostaddr[2])
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(hostaddr[4])
            s.listen(1)
            (conn, addr) = s.accept()
            logging.debug("App {}: Classical server started".format(self.name))
            self._classicalServer = conn

    def closeClassicalServer(self):
        if self._classicalServer:
            logging.debug("App {}: Closing classical server".format(self.name))
            self._classicalServer.close()
            logging.debug("App {}: Classical server closed".format(self.name))
            self._classicalServer = None

    def recvClassical(self, timout=1, msg_size=1024, close_after=True):
        if not self._classicalServer:
            self.startClassicalServer()
        for _ in range(10 * timout):
            logging.debug("App {}: Trying to receive classical message".format(self.name))
            msg = self._classicalServer.recv(msg_size)
            if len(msg) > 0:
                logging.debug("App {}: Received classical message".format(self.name))
                if close_after:
                    self.closeClassicalServer()
                return msg
            time.sleep(0.1)
        raise RuntimeError("Timeout: No message received")

    def openClassicalChannel(self, name):
        """
        Opens a classical connection to another host in the application network.

        - **Arguments**

            :name:        The name of the host in the application network.
            :timout:    The time to try to connect to the server. When timout is reached an RuntimeError is raised.
        """
        if self._appNet is None:
            raise ValueError(
                "Since use_classical_communication was set to False upon init, the built-in classical communication"
                "cannot be used."
            )
        if name not in self._classicalConn:
            logging.debug("App {}: Opening classical channel to {}".format(self.name, name))
            if name in self._appNet.hostDict:
                remoteHost = self._appNet.hostDict[name]
            else:
                raise ValueError("Host name '{}' is not in the cqc network".format(name))

            addr = remoteHost.addr
            while True:
                try:
                    s = socket.socket(addr[0], addr[1], addr[2])
                    s.connect(addr[4])
                    logging.debug("App {}: Classical channel to {} opened".format(self.name, name))
                    break
                except ConnectionRefusedError:
                    logging.debug(
                        "App {}: Could not open classical channel to {}, trying again..".format(self.name, name)
                    )
                    time.sleep(self._conn_retry_time)
                except Exception as e:
                    logging.warning(
                        "App {} : Critical error when connection to app node {}: {}".format(self.name, name, e)
                    )
                    break
            self._classicalConn[name] = s

    def closeClassicalChannel(self, name):
        """
        Closes a classical connection to another host in the application network.

        - **Arguments**

            :name:        The name of the host in the application network.
        """
        if name in self._classicalConn:
            logging.debug("App {}: Closing classical channel to {}".format(self.name, name))
            s = self._classicalConn.pop(name)
            s.close()
            logging.debug("App {}: Classical channel to {} closed".format(self.name, name))

    def sendClassical(self, name, msg, close_after=True):
        """
        Sends a classical message to another host in the application network.

        - **Arguments**

            :name:        The name of the host in the application network.
            :msg:        The message to send. Should be either a int in range(0,256) or a list of such ints.
            :timout:    The time to try to connect to the server. When timout is reached an RuntimeError is raised.
        """
        if name not in self._classicalConn:
            self.openClassicalChannel(name)
        try:
            to_send = bytes([int(msg)])
        except (TypeError, ValueError):
            to_send = bytes(msg)
        logging.debug("App {}: Sending classical message {} to {}".format(self.name, to_send, name))
        self._classicalConn[name].send(to_send)
        logging.debug("App {}: Classical message {} to {} sent".format(self.name, to_send, name))
        if close_after:
            self.closeClassicalChannel(name)

    def sendSimple(self, tp):
        """
        Sends a simple message to the cqc server, for example a HELLO message if tp=CQC_TP_HELLO.
        """
        hdr = CQCHeader()
        hdr.setVals(CQC_VERSION, tp, self._appID, 0)
        msg = hdr.pack()
        self._s.send(msg)

    def sendCommand(self, qID, command, notify=1, block=1, action=0):
        """
        Sends a simple message and command message to the cqc server.

        - **Arguments**

            :qID:        qubit ID
            :command:    Command to be executed, eg CQC_CMD_H
            :nofify:    Do we wish to be notified when done.
            :block:        Do we want the qubit to be blocked
            :action:    Are there more commands to be executed
        """
        # Send Header
        hdr = CQCHeader()
        hdr.setVals(CQC_VERSION, CQC_TP_COMMAND, self._appID, CQCCmdHeader.HDR_LENGTH)
        msg = hdr.pack()
        self._s.send(msg)

        # Send Command
        cmd_hdr = CQCCmdHeader()
        cmd_hdr.setVals(qID, command, notify, block, action)
        cmd_msg = cmd_hdr.pack()
        self._s.send(cmd_msg)

    def sendCmdXtra(
        self,
        qID,
        command,
        notify=1,
        block=1,
        action=0,
        xtra_qID=0,
        step=0,
        remote_appID=0,
        remote_node=0,
        remote_port=0,
        ref_id=0
    ):
        """
        Sends a simple message, command message and xtra message to the cqc server.

        - **Arguments**

            :qID:         qubit ID
            :command:     Command to be executed, eg CQC_CMD_H
            :nofify:     Do we wish to be notified when done.
            :block:         Do we want the qubit to be blocked
            :action:     Are there more commands to be executed
            :xtra_qID:     Extra qubit ID for for example CNOT
            :step:         Defines the angle of rotation.
            :remote_appID:     Application ID of remote host
            :remote_node:     ip of remote host in cqc network
            :remote_port:     port of remote host in cqc network
        """

        # Check what extra header we require
        xtra_hdr = None
        if command == CQC_CMD_SEND or command == CQC_CMD_EPR:
            xtra_hdr = CQCCommunicationHeader()
            xtra_hdr.setVals(remote_appID, remote_node, remote_port)
        elif command == CQC_CMD_CNOT or command == CQC_CMD_CPHASE:
            xtra_hdr = CQCXtraQubitHeader()
            xtra_hdr.setVals(xtra_qID)
        elif command == CQC_CMD_ROT_X or command == CQC_CMD_ROT_Y or command == CQC_CMD_ROT_Z:
            xtra_hdr = CQCRotationHeader()
            xtra_hdr.setVals(step)
        elif command == CQC_CMD_MEASURE or CQC_CMD_MEASURE_INPLACE:
            xtra_hdr = CQCAssignHeader()
            xtra_hdr.setVals(ref_id)

        if xtra_hdr is None:
            header_length = CQCCmdHeader.HDR_LENGTH
            xtra_msg = b""
        else:
            xtra_msg = xtra_hdr.pack()
            header_length = CQCCmdHeader.HDR_LENGTH + xtra_hdr.HDR_LENGTH

            # Send Header
        hdr = CQCHeader()
        hdr.setVals(CQC_VERSION, CQC_TP_COMMAND, self._appID, header_length)
        msg = hdr.pack()

        # Send Command
        cmd_hdr = CQCCmdHeader()
        cmd_hdr.setVals(qID, command, notify, block, action)
        cmd_msg = cmd_hdr.pack()

        # Send headers
        self._s.send(msg + cmd_msg + xtra_msg)

    def sendGetTime(self, qID, notify=1, block=1, action=0):
        """
        Sends get-time message

        - **Arguments**

            :qID:         qubit ID
            :command:     Command to be executed, eg CQC_CMD_H
            :notify:     Do we wish to be notified when done.
            :block:         Do we want the qubit to be blocked
            :action:     Are there more commands to be executed
        """
        # Send Header
        hdr = CQCHeader()
        hdr.setVals(CQC_VERSION, CQC_TP_GET_TIME, self._appID, CQCCmdHeader.HDR_LENGTH)
        msg = hdr.pack()
        self._s.send(msg)

        # Send Command
        cmd_hdr = CQCCmdHeader()
        cmd_hdr.setVals(qID, 0, notify, block, action)
        cmd_msg = cmd_hdr.pack()
        self._s.send(cmd_msg)

    def allocate_qubits(self, num_qubits, notify=True, block=True):
        """
        Requests the backend to reserve some qubits
        :param num_qubits: The amount of qubits to reserve
        :return: A list of qubits
        :param notify:     Do we wish to be notified when done.
        :param block:         Do we want the qubit to be blocked
        """

        # CQC header
        hdr = CQCHeader()
        hdr.setVals(CQC_VERSION, CQC_TP_COMMAND, self._appID, CQCCmdHeader.HDR_LENGTH)
        cqc_msg = hdr.pack()

        # Command header
        cmd_hdr = CQCCmdHeader()
        cmd_hdr.setVals(num_qubits, CQC_CMD_ALLOCATE, int(notify), int(block), 0)
        cmd_msg = cmd_hdr.pack()

        self._s.send(cqc_msg + cmd_msg)
        qubits = []
        for _ in range(num_qubits):
            msg = self.readMessage()
            self.check_error(msg[0])
            if msg[0].tp != CQC_TP_NEW_OK:
                print(len(msg))
                raise CQCUnsuppError("Unexpected message of type {} send back from backend".format(msg[0].tp))
            qubits.append(self.parse_CQC_msg(msg))
            self.print_CQC_msg(msg)
        if notify:
            message = self.readMessage()
            if message[0].tp != CQC_TP_DONE:
                raise CQCUnsuppError(
                    "Unexpected message send back from the server. Message: {}".format(message[0].printable())
                )

        return qubits

    def release_qubits(self, qubits, notify=True, block=True, action=False):
        """
        Release qubits so backend can free them up for other uses
        :param qubits: a list of qubits to be released
        :param notify:     Do we wish to be notified when done.
        :param block:         Do we want the qubit to be blocked
        :param action:     Execute the releases recursively or sequencely
        """

        if isinstance(qubits, qubit):
            qubits = [qubits]
        assert isinstance(qubits, list)
        n = len(qubits)

        if n == 0:  # then we don't need to do anything
            return

        logging.debug("App {} tells CQC: Release {} qubits".format(self.name, n))
        if action:
            hdr_length = CQCCmdHeader.HDR_LENGTH + CQCSequenceHeader.HDR_LENGTH
        else:
            hdr_length = CQCCmdHeader.HDR_LENGTH
        hdr = CQCHeader()
        hdr.setVals(CQC_VERSION, CQC_TP_COMMAND, self._appID, hdr_length * n)
        cqc_msg = hdr.pack()

        release_messages = b""

        for i in range(n):
            q = qubits[i]
            try:
                q.check_active()
            except QubitNotActiveError as e:
                raise QubitNotActiveError(
                    str(e) + ". Qubit {} is not active. None of the qubits are released".format(q._qID)
                )
            q._set_active(False)
            cmd_hdr = CQCCmdHeader()
            cmd_hdr.setVals(q._qID, CQC_CMD_RELEASE, int(notify), int(block), int(action))
            release_messages += cmd_hdr.pack()
            if action:
                seq_hdr = CQCSequenceHeader()
                # After this one we are sending n-i-1 more releases
                seq_hdr.setVals(hdr_length * (n - i - 1))
                release_messages += seq_hdr.pack()

        self._s.send(cqc_msg + release_messages)

        if notify:
            msg = self.readMessage()
            self.check_error(msg[0])
            if msg[0].tp != CQC_TP_DONE:
                raise CQCUnsuppError(
                    "Unexpected message sent back from the server. Message: {}".format(msg[0].printable())
                )
            self.print_CQC_msg(msg)

    def release_all_qubits(self):
        """
        Releases all qubits off this connection
        """
        return self.release_qubits(self.active_qubits[:])

    # sendFactory is depecrated. Use flush_factory() instead. #
    def sendFactory(
        self,
        qID,
        command,
        num_iter,
        notify=1,
        block=1,
        action=0,
        xtra_qID=-1,
        remote_appID=0,
        remote_node=0,
        remote_port=0,
        step_size=0,
    ):
        """
        Sends a factory message

        - **Arguments**

            :qID:         qubit ID
            :command:     Command to be executed, eg CQC_CMD_H
            :num_iter:     Number of times to execute command
            :nofify:     Do we wish to be notified when done.
            :block:         Do we want the factory to be blocked
            :action:     Are there more commands to be executed
            :xtra_qID:     Extra qubit ID for for example CNOT
            :remote_appID:     Application ID of remote host
            :remote_node:     ip of remote host in cqc network
            :remote_port:     port of remote host in cqc network
            :cmd_length:     length of extra commands
        """
        warnings.warn("Send factory is deprecated. Use flush_factory() instead", DeprecationWarning)

        if xtra_qID == -1:
            if command == CQC_CMD_CNOT or command == CQC_CMD_CPHASE:
                raise CQCUnsuppError("Please provide a target qubit")
            xtra_qID = 0

            # Check what extra header we require
        xtra_hdr = None
        if hasXtraHeader(command):
            if command == CQC_CMD_SEND or command == CQC_CMD_EPR:
                xtra_hdr = CQCCommunicationHeader()
                xtra_hdr.setVals(remote_appID, remote_node, remote_port)
            elif command == CQC_CMD_CNOT or command == CQC_CMD_CPHASE:
                xtra_hdr = CQCXtraQubitHeader()
                xtra_hdr.setVals(xtra_qID)
            else:
                xtra_hdr = CQCRotationHeader()
                xtra_hdr.setVals(step_size)
            xtra_msg = xtra_hdr.pack()
            hdr_length = CQCCmdHeader.HDR_LENGTH + CQCFactoryHeader.HDR_LENGTH + xtra_hdr.HDR_LENGTH
        else:
            xtra_msg = b""
            hdr_length = CQCCmdHeader.HDR_LENGTH + CQCFactoryHeader.HDR_LENGTH

            # Send Header
        hdr = CQCHeader()
        hdr.setVals(CQC_VERSION, CQC_TP_FACTORY, self._appID, hdr_length)
        msg = hdr.pack()

        # Factory header
        factory_hdr = CQCFactoryHeader()
        factory_hdr.setVals(num_iter, notify, block)
        factory_msg = factory_hdr.pack()

        # Send Command
        cmd_hdr = CQCCmdHeader()
        cmd_hdr.setVals(qID, command, 0, block, action)
        cmd_msg = cmd_hdr.pack()
        logging.debug("App {} sends CQC message {}".format(self.name, hdr.printable()))
        logging.debug("App {} sends CQC message {}".format(self.name, factory_hdr.printable()))

        logging.debug("App {} sends CQC message {}".format(self.name, cmd_hdr.printable()))
        if xtra_hdr:
            logging.debug("App {} sends CQC message {}".format(self.name, xtra_hdr.printable()))
        self._s.send(msg + factory_msg + cmd_msg + xtra_msg)

        # Get RECV messages
        # Some commands expect to get a list of messages back, check those
        res = []
        if shouldReturn(command):
            for _ in range(num_iter):
                message = self.readMessage()
                if message[0].tp in {CQC_TP_NEW_OK, CQC_TP_RECV, CQC_TP_EPR_OK}:
                    qID = message[1].qubit_id
                    q = qubit(self, createNew=False, q_id=qID, notify=notify, block=block)
                    q._set_active(True)
                    res.append(q)
                elif message[0].tp == CQC_TP_MEASOUT:
                    outcome = message[1].outcome
                    res.append(outcome)
        if notify:
            message = self.readMessage()
            if message[0].tp != CQC_TP_DONE:
                raise CQCUnsuppError(
                    "Unexpected message send back from the server. Message: {}".format(message[0].printable())
                )
        return res

    def readMessage(self, maxsize=192):  # WHAT IS GOOD SIZE?
        """
        Receive the whole message from cqc server.
        Returns (CQCHeader,None,None), (CQCHeader,CQCNotifyHeader,None) or (CQCHeader,CQCNotifyHeader,EntInfoHeader)
        depending on the type of message.
        Maxsize is the max size of message.
        """

        # Initilize checks
        gotCQCHeader = False
        if self.buf:
            checkedBuf = False
        else:
            checkedBuf = True

        while True:
            # If buf does not contain enough data, read in more
            if checkedBuf:
                # Receive data
                data = self._s.recv(maxsize)

                # Read whatever we received into a buffer
                if self.buf:
                    self.buf += data
                else:
                    self.buf = data

                    # If we don't have the CQC header yet, try and read it in full.
            if not gotCQCHeader:
                if len(self.buf) < CQCHeader.HDR_LENGTH:
                    # Not enough data for CQC header, return and wait for the rest
                    checkedBuf = True
                    continue

                    # Got enough data for the CQC Header so read it in
                gotCQCHeader = True
                rawHeader = self.buf[0:CQCHeader.HDR_LENGTH]
                currHeader = CQCHeader(rawHeader)

                # Remove the header from the buffer
                self.buf = self.buf[CQCHeader.HDR_LENGTH : len(self.buf)]

                # Check for error
                self.check_error(currHeader)

                # Check whether we already received all the data
            if len(self.buf) < currHeader.length:
                # Still waiting for data
                checkedBuf = True
                continue
            else:
                break
                # We got all the data, read other headers if there is any
        if currHeader.length == 0:
            return currHeader, None, None
        else:
            if currHeader.tp == CQC_TP_INF_TIME:
                timeinfo_header = self._extract_header(CQCTimeinfoHeader)
                return currHeader, timeinfo_header, None
            elif currHeader.tp == CQC_TP_MEASOUT:
                measout_header = self._extract_header(CQCMeasOutHeader)
                return currHeader, measout_header, None
            elif currHeader.tp in [CQC_TP_RECV, CQC_TP_NEW_OK, CQC_TP_EXPIRE]:
                xtra_qubit_header = self._extract_header(CQCXtraQubitHeader)
                return currHeader, xtra_qubit_header, None
            elif currHeader.tp == CQC_TP_EPR_OK:
                xtra_qubit_header = self._extract_header(CQCXtraQubitHeader)
                ent_info_hdr = self._extract_header(EntInfoHeader)
                return currHeader, xtra_qubit_header, ent_info_hdr

    def _extract_header(self, header_class):
        """
        Extracts the given header class from the first part of the current buffer.
        :param header_class: Subclassed from `cqc.backend.cqcHeader.Header`
        :return: An instance of the class
        """
        if not issubclass(header_class, Header):
            raise ValueError("header_class {} is not a subclass of Header".format(header_class))

        try:
            rawHeader = self.buf[:header_class.HDR_LENGTH]
        except IndexError:
            raise ValueError("Got a header message of unexpected size")
        self.buf = self.buf[header_class.HDR_LENGTH: len(self.buf)]
        header = header_class(rawHeader)

        return header

    def print_CQC_msg(self, message):
        """
        Prints messsage returned by the readMessage method of CQCConnection.
        """
        hdr = message[0]
        otherHdr = message[1]
        entInfoHdr = message[2]

        if hdr.tp == CQC_TP_HELLO:
            logging.debug("CQC tells App {}: 'HELLO'".format(self.name))
        elif hdr.tp == CQC_TP_EXPIRE:
            logging.debug("CQC tells App {}: 'Qubit with ID {} has expired'".format(self.name, otherHdr.qubit_id))
        elif hdr.tp == CQC_TP_DONE:
            logging.debug("CQC tells App {}: 'Done with command'".format(self.name))
        elif hdr.tp == CQC_TP_RECV:
            logging.debug("CQC tells App {}: 'Received qubit with ID {}'".format(self.name, otherHdr.qubit_id))
        elif hdr.tp == CQC_TP_EPR_OK:

            # Lookup host name
            remote_node = entInfoHdr.node_B
            remote_port = entInfoHdr.port_B
            remote_name = None
            try:
                for node in self._cqcNet.hostDict.values():
                    if (node.ip == remote_node) and (node.port == remote_port):
                        remote_name = node.name
                        break
                if remote_name is None:
                    raise RuntimeError("Remote node ({},{}) is not in config-file.".format(remote_node, remote_port))
            except AttributeError:
                remote_name = "({}, {})".format(remote_node, remote_port)

            logging.debug(
                "CQC tells App {}: 'EPR created with node {}, using qubit with ID {}'".format(
                    self.name, remote_name, otherHdr.qubit_id
                )
            )
        elif hdr.tp == CQC_TP_MEASOUT:
            logging.debug("CQC tells App {}: 'Measurement outcome is {}'".format(self.name, otherHdr.outcome))
        elif hdr.tp == CQC_TP_INF_TIME:
            logging.debug("CQC tells App {}: 'Timestamp is {}'".format(self.name, otherHdr.datetime))

    def parse_CQC_msg(self, message, q=None, is_factory=False):
        """
        parses the cqc message and returns the relevant value of that measure
        (qubit, measurement outcome)

        :param message: str
            the cqc message to be parsed
        :param q: :obj:`cqc.pythonLib.qubit`
            the qubit object we should save the qubit to
        :param is_factory: bool
            whether the returned message came from a factory. If so, do not change the qubit, but create a new one
        :return: the result of the message (either a qubit, or a measurement outcome. Otherwise None
        """
        hdr = message[0]
        otherHdr = message[1]
        entInfoHdr = message[2]

        if hdr.tp in {CQC_TP_RECV, CQC_TP_NEW_OK, CQC_TP_EPR_OK}:
            if is_factory:
                q._set_active(False)  # Set qubit to inactive so it can't be used anymore
                q = qubit(self, createNew=False)
            if q is None:
                q = qubit(self, createNew=False)
            q._qID = otherHdr.qubit_id
            q.set_entInfo(entInfoHdr)
            q._set_active(True)
            return q
        if hdr.tp == CQC_TP_MEASOUT:
            return otherHdr.outcome
        if hdr.tp == CQC_TP_INF_TIME:
            return otherHdr.datetime

    def check_error(self, hdr):
        """
        Checks if there is an error returned.
        """
        self._errorHandler(hdr.tp)

    def _errorHandler(self, cqc_err):
        """
        Raises an error if there is an error-message
        """
        if cqc_err == CQC_ERR_GENERAL:
            raise CQCGeneralError("General error")
        if cqc_err == CQC_ERR_NOQUBIT:
            raise CQCNoQubitError("No more qubits available")
        if cqc_err == CQC_ERR_UNSUPP:
            raise CQCUnsuppError("Sequence not supported")
        if cqc_err == CQC_ERR_TIMEOUT:
            raise CQCTimeoutError("Timeout")
        if cqc_err == CQC_ERR_UNKNOWN:
            raise CQCUnknownError("Unknown qubit ID")

    def sendQubit(self, q, name, remote_appID=0, remote_socket=None, notify=True, block=True):
        """
        Sends qubit to another node in the cqc network. If this node is not in the network an error is raised.

        - **Arguments**

            :q:         The qubit to send.
            :Name:         Name of the node as specified in the cqc network config file.
            :remote_appID:     The app ID of the application running on the receiving node.
            :remote_socket: tuple (str, int) of ip and port number. Needed if no cqcFile was specified
            :nofify:     Do we wish to be notified when done.
            :block:         Do we want the qubit to be blocked
        """
        remote_ip, remote_port = get_remote_from_directory_or_address(self._cqcNet, name, remote_socket)

        if self.pend_messages:

            # Build command header and communication sub header
            command_header = CQCCmdHeader()
            command_header.setVals(q._qID, CQC_CMD_SEND, notify, block)

            comm_sub_header = CQCCommunicationHeader()
            comm_sub_header.setVals(remote_appID, remote_ip, remote_port)

            # Pend header
            self._pend_header(command_header)
            self._pend_header(comm_sub_header)

            # Deactivate qubit
            q._set_active(False)

            # print info
            logging.debug(
                "App {} pends message: 'Send qubit with ID {} to {} and appID {}'".format(
                    self.name, q._qID, name, remote_appID
                )
            )
        else:
            # print info
            logging.debug(
                "App {} tells CQC: 'Send qubit with ID {} to {} and appID {}'".format(
                    self.name, q._qID, name, remote_appID
                )
            )
            self.sendCmdXtra(
                q._qID,
                CQC_CMD_SEND,
                notify=int(notify),
                block=int(block),
                remote_appID=remote_appID,
                remote_node=remote_ip,
                remote_port=remote_port,
            )
            if notify:
                message = self.readMessage()
                self.print_CQC_msg(message)
            
            # Deactivate qubit
            q._set_active(False)

    def recvQubit(self, notify=True, block=True):
        """
        Receives a qubit.

        - **Arguments**

            :q:         The qubit to send.
            :Name:         Name of the node as specified in the cqc network config file.
            :remote_appID:     The app ID of the application running on the receiving node.
            :nofify:     Do we wish to be notified when done.
            :block:         Do we want the qubit to be blocked
        """

        if self.pend_messages:
            # print info
            logging.debug("App {} pends message: 'Receive qubit'".format(self.name))

            # Build header
            header = CQCCmdHeader()
            header.setVals(0, CQC_CMD_RECV, notify, block)

            # Pend header
            self._pend_header(header)

        else:
            # print info
            logging.debug("App {} tells CQC: 'Receive qubit'".format(self.name))
            self.sendCommand(0, CQC_CMD_RECV, notify=int(notify), block=int(block))

            # Get RECV message
            message = self.readMessage()
            otherHdr = message[1]
            q_id = otherHdr.qubit_id

            self.print_CQC_msg(message)

            if notify:
                message = self.readMessage()
                self.print_CQC_msg(message)

            # initialize the qubit
            q = qubit(self, createNew=False)
            q._qID = q_id

            # Activate and return qubit
            q._set_active(True)
            return q

    def createEPR(self, name, remote_appID=0, remote_socket=None, notify=True, block=True):
        """
        Creates epr with other host in cqc network.

        - **Arguments**

            :name:         Name of the node as specified in the cqc network config file.
            :remote_appID:     The app ID of the application running on the receiving node.
            :remote_socket: tuple (str, int) of ip and port number. Needed if no cqcFile was specified
            :nofify:     Do we wish to be notified when done.
            :block:         Do we want the qubit to be blocked
        """

        remote_ip, remote_port = get_remote_from_directory_or_address(self._cqcNet, name, remote_socket)

        if self.pend_messages:

            # Build command header and communication sub header
            command_header = CQCCmdHeader()
            command_header.setVals(0, CQC_CMD_EPR, notify, block)

            comm_sub_header = CQCCommunicationHeader()
            comm_sub_header.setVals(remote_appID, remote_ip, remote_port)

            # Pend header
            self._pend_header(command_header)
            self._pend_header(comm_sub_header)

            # print info
            logging.debug(
                "App {} pends message: 'Create EPR-pair with {} and appID {}'".format(self.name, name, remote_appID)
            )

        else:
            # print info
            logging.debug(
                "App {} tells CQC: 'Create EPR-pair with {} and appID {}'".format(self.name, name, remote_appID)
            )

            self.sendCmdXtra(
                0,
                CQC_CMD_EPR,
                notify=int(notify),
                block=int(block),
                remote_appID=remote_appID,
                remote_node=remote_ip,
                remote_port=remote_port,
            )
            # Get RECV message
            message = self.readMessage()
            otherHdr = message[1]
            entInfoHdr = message[2]
            q_id = otherHdr.qubit_id

            self.print_CQC_msg(message)

            if notify:
                message = self.readMessage()
                self.print_CQC_msg(message)

            # initialize the qubit
            q = qubit(self, createNew=False)

            q.set_entInfo(entInfoHdr)
            q._qID = q_id
            # Activate and return qubit
            q._set_active(True)
            return q

    def recvEPR(self, notify=True, block=True):
        """
        Receives a qubit from an EPR-pair generated with another node.

        - **Arguments**

            :nofify:     Do we wish to be notified when done.
            :block:         Do we want the qubit to be blocked
        """

        if self.pend_messages:

            # Build header
            header = CQCCmdHeader()
            header.setVals(0, CQC_CMD_EPR_RECV, notify, block)

            # Pend header
            self._pend_header(header)

            # print info
            logging.debug("App {} pends message: 'Receive half of EPR'".format(self.name))

        else:
            # print info
            logging.debug("App {} tells CQC: 'Receive half of EPR'".format(self.name))
            self.sendCommand(0, CQC_CMD_EPR_RECV, notify=int(notify), block=int(block))

            # Get RECV message
            message = self.readMessage()
            otherHdr = message[1]
            entInfoHdr = message[2]
            q_id = otherHdr.qubit_id

            self.print_CQC_msg(message)

            if notify:
                message = self.readMessage()
                self.print_CQC_msg(message)

            # initialize the qubit
            q = qubit(self, createNew=False)

            q.set_entInfo(entInfoHdr)
            q._qID = q_id

            # Activate and return qubit
            q._set_active(True)
            return q

    def set_pending(self, pend_messages):
        """
        Set the pend_messages flag.
        If true, flush() has to be called to send all self._pending_headers in sequence to the backend
        If false, all commands are directly send to the back_end
        :param pend_messages: Boolean to indicate if messages should pend or not
        """
        # Check if the list is not empty, give a warning if it isn't
        if self._pending_headers:
            logging.warning("List of pending headers is not empty, flushing them")
            self.flush()
        self.pend_messages = pend_messages

    def create_qubits(self, nb_of_qubits: int) -> List['qubit']:
        """
        Creates (i.e. allocates) multiple qubits, and returns a list with qubit objects.
        :nb_of_qubits: The amount of qubits to be created.
        """
        # First, flush all pending headers
        self.flush()

        # Build and insert the new qubit Command header
        cmd_header = CQCCmdHeader()
        cmd_header.setVals(qubit_id=0, instr=CQC_CMD_NEW, notify=1, block=1)
        self._pend_header(cmd_header)
        
        return self.flush_factory(nb_of_qubits)

    def flush(self, do_sequence=False):
        """
        Flush all pending messages to the backend.
        :param do_sequence: boolean to indicate if you want to send the pending messages as a sequence
        :return: A list of things that are sent back from the server. Can be qubits, or outcomes
        """
        return self.flush_factory(1, do_sequence)

    def flush_factory(self, num_iter, do_sequence=False, block_factory=False):
        """
        Flushes the current pending sequence in a factory. It is performed multiple times
        :param num_iter: The amount of times the current pending sequence is performed
        :return: A list of outcomes/qubits that are produced by the commands
        """

        # Initialize should_notify to False
        should_notify = False

        # Store how many of the headers we send will get a response message from the backend
        response_amount = 0

        # Loop over the pending_headers to determine the total length and set should_notify
        for header in self._pending_headers:

            # Check if the current header is a Command header. It can also be a sub header
            if isinstance(header, CQCCmdHeader):
                # set should_notify to True if at least one of all command headers has notify to True
                should_notify = should_notify or header.notify
                
                # Remember this header if we expect a return messge
                if shouldReturn(header.instr):
                    response_amount += 1

        # Determine the CQC Header type
        if num_iter == 1:
            cqc_type = CQC_TP_COMMAND
        else:
            # Build and insert the Factory header
            cqc_type = CQC_TP_FACTORY
            factory_header = CQCFactoryHeader()
            factory_header.setVals(num_iter, should_notify, block_factory)
            # Insert the factory header at the front
            self._pending_headers.insert(0, factory_header)
            
        # Insert the cqc header
        self.insert_cqc_header(cqc_type)
        
        # Send all pending headers
        self.send_pending_headers()

        # Read out any returned messages from the backend
        res = []
        for _ in range(num_iter):
            for _ in range(response_amount):
                message = self.readMessage()
                self.check_error(message[0])
                res.append(self.parse_CQC_msg(message))
                self.print_CQC_msg(message)
        
        if should_notify:
            message = self.readMessage()
            self.check_error(message[0])
        
        # Return information that the backend returned
        return res

    def send_pending_headers(self) -> List[Any]:
        """
        Sends all pending headers.
        After sending, self._pending_headers is emptied.
        """

        # Send all pending headers
        for header in self._pending_headers:
            self._s.send(header.pack())
            logging.debug("App {} sends CQC: {}".format(self.name, header.printable()))

        # Reset _pending_headers to an empty list after all headers are sent
        self._pending_headers = []

    def insert_cqc_header(self, cqc_type: CQCType, version=CQC_VERSION) -> None:
        """
        Inserts a CQC Header at index 0 of self._pending_headers.
        Invoke this method *after* all other headers are pended, so that the correct message length is calculated.
        """

        # Count the total message length
        message_length = 0
        for header in self._pending_headers:
            message_length += header.HDR_LENGTH

        # Build the CQC Header
        cqc_header = CQCHeader()
        cqc_header.setVals(CQC_VERSION, cqc_type, self._appID, message_length)

        # Insert CQC Header at the front
        self._pending_headers.insert(0, cqc_header)

    def _pend_type_header(self, cqc_type: CQCType, length: int) -> None:
        """
        Creates a CQCTypeHeader and pends it.
        """
        header = CQCTypeHeader()
        header.setVals(cqc_type, length)
        self._pend_header(header)

    def tomography(self, preparation, iterations, progress=True):
        """
        Does a tomography on the output from the preparation specified.
        The frequencies from X, Y and Z measurements are returned as a tuple (f_X,f_Y,f_Z).

        - **Arguments**

            :preparation:     A function that takes a CQCConnection as input and prepares a qubit and returns this
            :iterations:     Number of measurements in each basis.
            :progress_bar:     Displays a progress bar
        """
        accum_outcomes = [0, 0, 0]
        if progress:
            bar = ProgressBar(3 * iterations)

            # Measure in X
        for _ in range(iterations):
            # Progress bar
            if progress:
                bar.increase()

                # prepare and measure
            q = preparation(self)
            q.H()
            m = q.measure()
            accum_outcomes[0] += m

            # Measure in Y
        for _ in range(iterations):
            # Progress bar
            if progress:
                bar.increase()

                # prepare and measure
            q = preparation(self)
            q.K()
            m = q.measure()
            accum_outcomes[1] += m

            # Measure in Z
        for _ in range(iterations):
            # Progress bar
            if progress:
                bar.increase()

                # prepare and measure
            q = preparation(self)
            m = q.measure()
            accum_outcomes[2] += m

        if progress:
            bar.close()
            del bar

        freqs = map(lambda x: x / iterations, accum_outcomes)
        return list(freqs)

    def test_preparation(self, preparation, exp_values, conf=2, iterations=100, progress=True):
        """
        Test the preparation of a qubit.
        Returns True if the expected values are inside the confidence interval produced from the data received from
        the tomography function

        - **Arguments**

            :preparation:     A function that takes a CQCConnection as input and prepares a qubit and returns this
            :exp_values:     The expected values for measurements in the X, Y and Z basis.
            :conf:         Determines the confidence region (+/- conf/sqrt(iterations) )
            :iterations:     Number of measurements in each basis.
            :progress_bar:     Displays a progress bar
        """
        epsilon = conf / math.sqrt(iterations)

        freqs = self.tomography(preparation, iterations, progress=progress)
        for i in range(3):
            if abs(freqs[i] - exp_values[i]) > epsilon:
                print(freqs, exp_values, epsilon)
                return False
        return True


class CQCVariable:
    """
    Instances of this class are returned by measure command, if executed inside a CQCMix context.
    A CQCVariable holds a reference ID with which one can refer to the outcome of the measurement.
    """
    _next_ref_id = 0
    
    def __init__(self):
        """
        Increments the reference ID, and assigns the new unique reference ID to this CQCVariable.
        This system ensures no two CQCVariable instances have the same reference ID.
        """
        self._ref_id = CQCVariable._next_ref_id
        CQCVariable._next_ref_id += 1

    # make ref_id a read-only variable
    @property
    def ref_id(self):
        """
        Get the refernce ID of this CQCVariable. This is a read-only property.
        """
        return self._ref_id

    # override the == operator
    # other can be a CQCVariable or int
    def __eq__(self, other: Union['CQCVariable', int]):
        return _LogicalFunction(self, CQCLogicalOperator.EQ, other)
    
    # override the != operator
    def __ne__(self, other: Union['CQCVariable', int]):
        return _LogicalFunction(self, CQCLogicalOperator.NEQ, other)
        

class _LogicalFunction:
    """
    Private helper class. This class should never be used outside this pythonLib.
    """

    def __init__(
        self, 
        operand_one: CQCVariable, 
        operator: CQCLogicalOperator, 
        operand_two: Union[CQCVariable, int]
    ):
        """
        Stores all information necessary to create a logical comparison

        - **Arguments**

            :operand_one:   The CQCVariable that stores the measurement outcome that must be compared
            :operator:      One of the CQCLogicalOperator types that CQC supports. 
                            At present, equality and inequality are supported.
            :operand_two:   Either a CQCVariable or an integer. 
                            If a CQCVariable, then the value behind this variable will be compared to operand_one. 
                            If an integer, then the value behind operand_one will be compared to this integer.
        """

        self.operand_one = operand_one
        self.operator = operator
        self.operand_two = operand_two

    def get_negation(self) -> '_LogicalFunction':
        return _LogicalFunction(self.operand_one, CQCLogicalOperator.opposite_of(self.operator), self.operand_two)

    def get_CQCIfHeader(self) -> CQCIfHeader:
        """
        Builds the If header corresponding to this logical function.
        """

        if isinstance(self.operand_two, int):
            type_of_operand_two = CQCIfHeader.TYPE_VALUE
            operand_two = self.operand_two
        else:
            type_of_operand_two = CQCIfHeader.TYPE_REF_ID
            operand_two = self.operand_two._ref_id

        header = CQCIfHeader()
        header.setVals(
            self.operand_one.ref_id,
            self.operator,
            type_of_operand_two,
            operand_two,
            length=0
        )
        return header


class CQCMix(NodeMixin):
    """
    This Python Context Manager Type can be used to create CQC programs that consist of more than a single type.
    Hence the name CQC Mix. Programs of this type can consist of any number and mix of the other CQC types. 
    """

    def __init__(self, cqc_connection: CQCConnection):
        """
        Initializes the Mix context.

        - **Arguments**

            :cqc_connection:    The CQCConnection to which this CQC Program must be sent.
        """

        self._conn = cqc_connection

        # Set the current scope to self
        self._conn.current_scope = self

    def __enter__(self):
        # Set the _inside_cqc_mix bool to True on the connection
        self._conn._inside_cqc_mix = True

        self._conn.pend_messages = True

        # Return self so that this instance is bound to the variable after "as", i.e.: "with CQCMix() as pgrm"
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        
        # Only do these things if there was no exception.
        if exc_type is None:
            # Build and insert the CQC Header
            self._conn.insert_cqc_header(CQCType.MIX)

            # Send this program to the backend
            self._conn.send_pending_headers()

            # We expect one message back, which can be an error or TP_DONE
            # This also blocks the program until we have received a message from the backend, 
            # which is important because it avoids that we send more messages before the backend is finished.
            message = self._conn.readMessage()

            # Check if it is an error and assume it is a TP_DONE if it is not an error
            self._conn.check_error(message[0])

            # We are no longer in a TP_MIX
            self._conn._inside_cqc_mix = False

            self._conn.pend_messages = False

            # Set the current scope to None, since we exit the CQCMix context 
            # current_scope is only used inside CQCMix contexts
            self._conn.current_scope = None

    def cqc_if(self, logical_function: _LogicalFunction):
        """
        Open a Python Context Manager Type to start an if-statement block.

        - **Arguments**

            :logical_function:      A _LogicalFunction instance. Never instantiate this explicitely; instead
                                    use the following: CQCVariable == 1 OR CQCVariable == CQCVariable. 
                                    CQCVariable can be any instance that you want to test to a value, or to another  
                                    CQCVariable. The operator can be == or !=. 
                                    The value can be any integer (though only 1 and 0 make sense).
                                
        """
        return _CQCConditional(self._conn, False, logical_function)

    def cqc_else(self):
        """
        Open a Python Context Manager Type to start an else-statement block.
        This will be  an else-block of the last closed cqc_if-block.                    
        """
        # Find out to which if this else belongs
        return _CQCConditional(self._conn, True)

    def loop(self, times: int):
        """
        Open a Python Context Manager Type to start a factory (i.e. repeated sequence of commands).

        - **Arguments**

            :times:     The number of times the commands inside body of this context should be repeated.
                                
        """
        return _CQCFactory(self._conn, times)


class _CQCFactory:
    """
    Private class to create factories inside CQCMix contexts. Never explicitely instantiate this class outside 
    the source code of this library.
    Instead, use CQCMix.loop(x), where x is the amount of times to repeat.
    """

    def __init__(self, cqc_connection: CQCConnection, repetition_amount: int):
        self._conn = cqc_connection
        self._repetition_amount = repetition_amount

    def __enter__(self):

        # Inside a TP_FACTORY, we don't want CQCType headers before every instruction.
        # Therefore, we set this bool to False
        self._conn._inside_cqc_mix = False

        # Create the CQC Type header, and store it so that we can modify its length at __exit__
        self.type_header = CQCTypeHeader()
        self.type_header.setVals(CQCType.FACTORY, length=0)

        # Build the Factory header
        factory_header = CQCFactoryHeader()
        factory_header.setVals(self._repetition_amount)

        # Pend the headers
        self._conn._pend_header(self.type_header)
        self._conn._pend_header(factory_header)

    def __exit__(self, exc_type, exc_val, exc_tb):

        # Outside a TP_FACTORY, we want CQCType headers before every instruction.
        # Therefore, we set this bool to True
        self._conn._inside_cqc_mix = True

        # Calculate the length of the body of the factory
        # Loop in reverse through all pending_headers to calculate the length of all headers
        index = len(self._conn._pending_headers) - 1
        body_length = 0
        while self._conn._pending_headers[index] is not self.type_header:
            body_length += self._conn._pending_headers[index].HDR_LENGTH
            index -= 1
        
        # Set the correct length
        self.type_header.length = body_length


class _CQCConditional(NodeMixin):
    """
    Private helper class. Never explicitely instantiate this class outside the source code of this library.
    This Context Manager class is instantiated by CQCMix.cqc_if() and CQCMix.cqc_else(). Its 
    function is to build and pend CQC If headers.
    """

    # This private class variable holds the last _CQCConditional that 
    # functioned as an IF (as opposed to an ELSE) on which __exit__ is invoked. 
    # In other words, it is the last closed IF statement. 
    # This is important so that ELSE statements can find out to which IF statement they belong.
    # If this variable is None, then there either has not been aan IF statement yet, or the last 
    # _CQCConditional was an ELSE.
    _last_closed_conditional = None

    def __init__(self, cqc_connection: CQCConnection, is_else: bool, logical_function: _LogicalFunction = None):
        self._conn = cqc_connection
        self.is_else = is_else

        if is_else:
            # If _last_closed_conditional is None, then there either has not been aan IF statement yet, or the last 
            # _CQCConditional was an ELSE.
            if _CQCConditional._last_closed_conditional is None:
                raise CQCGeneralError('Cannot use an ELSE if there is no IF directly before it.')
            else:
                # Get the negation of the logical function of the IF, 
                # which will be the logical function for this ELSE statement
                logical_function = _CQCConditional._last_closed_conditional._logical_function.get_negation()
            
        self._logical_function = logical_function

    def __enter__(self):
        # Pend CQC Type header
        self._conn._pend_type_header(CQCType.IF, CQCIfHeader.HDR_LENGTH)

        # Build the IF header, and store it so we can modify its length at __exit__
        self.header = self._logical_function.get_CQCIfHeader()

        # Pend the IF header
        self._conn._pend_header(self.header)

        # Register the parent scope, and set the current scope to self
        self.parent = self._conn.current_scope
        self._conn.current_scope = self

    def __exit__(self, exc_type, exc_val, exc_tb):

        # Set _last_closed_conditional to the correct value
        if (self.is_else):
            _CQCConditional._last_closed_conditional = None
        else:
            _CQCConditional._last_closed_conditional = self

        # Calculate the length of the body of the conditional
        # Loop in reverse through all pending_headers to calculate the lenght of all headers
        index = len(self._conn._pending_headers) - 1
        body_length = 0
        while self._conn._pending_headers[index] is not self.header:
            body_length += self._conn._pending_headers[index].HDR_LENGTH
            index -= 1
        
        # Set the correct length
        self.header.length = body_length
            
        # Set the scope to the parent scope
        self._conn.current_scope = self.parent


class ProgressBar:
    def __init__(self, maxitr):
        self.maxitr = maxitr
        self.itr = 0
        try:
            self.cols = os.get_terminal_size().columns
        except (OSError, AttributeError):
            self.cols = 60
        print("")
        self.update()

    def increase(self):
        self.itr += 1
        self.update()

    def update(self):
        cols = self.cols - 8
        assert self.itr <= self.maxitr
        ratio = float(self.itr) / self.maxitr
        procent = int(ratio * 100)
        progress = "=" * int(cols * ratio)
        sys.stdout.write("\r")
        sys.stdout.write("[%*s] %d%%" % (-cols, progress, procent))
        sys.stdout.flush()
        pass

    def close(self):
        print("")


class CQCGeneralError(Exception):
    pass


class CQCNoQubitError(CQCGeneralError):
    pass


class CQCUnsuppError(CQCGeneralError):
    pass


class CQCTimeoutError(CQCGeneralError):
    pass


class CQCInuseError(CQCGeneralError):
    pass


class CQCUnknownError(CQCGeneralError):
    pass


class QubitNotActiveError(CQCGeneralError):
    pass


class qubit:
    """
    A qubit.
    """

    def __init__(self, cqc, notify=True, block=True, createNew=True, q_id=None, entInfo=None):
        """
        Initializes the qubit. The cqc connection must be given.
        If notify, the return message is received before the method finishes.
        createNew is set to False when we receive a qubit.

        - **Arguments**

            :cqc:         The CQCconnection used
            :nofify:     Do we wish to be notified when done.
            :block:         Do we want the qubit to be blocked
            :createNew:     If NEW-message should be sent, used internally
            :q_id:         Qubit id, used internally if createNew
            :entInfo:     Entanglement information, if qubit is part of EPR-pair
        """

        # Cqc connection
        self._cqc = cqc

        # Check if the cqc connection was openened using a 'with' statement
        # If not, raise a deprecation warning
        if not self._cqc._opened_with_with:
            logging.warning(
                "You should open CQCConnection in a context, i.e. using 'with CQCConnection(...) as cqc:'. "
                "Then qubits will be automatically released by the end of the program, independently of what happens. "
                "For more information, see https://softwarequtech.github.io/SimulaQron/html/PythonLib.html"
            )

        # Whether the qubit is active. Will be set in the first run
        self._active = None

        # This stores the scope (type NodeMixin) in which this qubit was deactivated
        # If the qubit has not yet been deactivated, this is set to None
        self.scope_of_deactivation = None

        if createNew:
            # print info
            logging.debug("App {} tells CQC: 'Create qubit'".format(self._cqc.name))

            # Create new qubit at the cqc server
            self._cqc.sendCommand(0, CQC_CMD_NEW, notify=int(notify), block=int(block))

            # Get qubit id
            message = self._cqc.readMessage()
            try:
                otherHdr = message[1]
                self._qID = otherHdr.qubit_id
            except AttributeError:
                raise CQCGeneralError("Didn't receive the qubit id")
                # Activate qubit
            self._set_active(True)

            if notify:
                message = self._cqc.readMessage()
                self._cqc.print_CQC_msg(message)
        else:
            self._qID = q_id
            self._set_active(False)  # Why?

        # Entanglement information
        self._entInfo = entInfo

        # Lookup remote entangled node
        self._remote_entNode = None
        if self._entInfo:
            ip = self._entInfo.node_B
            port = self._entInfo.port_B
            try:
                for node in self._cqc._cqcNet.hostDict.values():
                    if (node.ip == ip) and (node.port == port):
                        self._remote_entNode = node.name
                        break
            except AttributeError:
                self._remote_entNode = None

    def __str__(self):
        if self._active:
            return "Qubit at the node {}".format(self._cqc.name)
        else:
            return "Not active qubit"

    def get_entInfo(self):
        return self._entInfo

    def print_entInfo(self):
        if self._entInfo:
            print(self._entInfo.printable())
        else:
            print("No entanglement information")

    def set_entInfo(self, entInfo):
        self._entInfo = entInfo

        # Lookup remote entangled node
        self._remote_entNode = None
        if self._entInfo:
            ip = self._entInfo.node_B
            port = self._entInfo.port_B
            try:
                for node in self._cqc._cqcNet.hostDict.values():
                    if (node.ip == ip) and (node.port == port):
                        self._remote_entNode = node.name
                        break
            except AttributeError:
                self._remote_entNode = None

    def is_entangled(self):
        if self._entInfo:
            return True
        return False

    def get_remote_entNode(self):
        return self._remote_entNode

    def check_active(self):
        """
        Checks if the qubit is active
        """
        if not self._active:

            # This conditional checks whether it is certain that the qubit is inactive at this 
            # point in the code. If such is the case, an error is raised. 
            # At this point, it is certain that self_active is False. However, this does not necessarily
            # mean that the qubit is inactive due to the possibility to write cqc_if blocks.
            # There are four options:
            # 1) Control is currently not inside a CQCMix. In that case, the qubit is inactive.
            # 2) The qubit was deactivated in the current scope. The qubit therefore is inactive.
            # 3) The qubit was deactivated in an ancestor scope. The qubit therefore is inactive.
            # 4) The qubit was deactivated in a descendent scope.  The qubit is therefore inactive. 
            # The only possible way self_active can be False but the qubit is in fact active, is
            # if the qubit was deactivated in a sibling scope, such as the sibling if-block of an else-block.
            if (
                not self._cqc._inside_cqc_mix
                or self.scope_of_deactivation == self._cqc.current_scope
                or self.scope_of_deactivation in self._cqc.current_scope.ancestors
                or self.scope_of_deactivation in self._cqc.current_scope.descendants
            ):

                raise QubitNotActiveError(
                    "Qubit is not active. Possible causes:\n"
                    "- Qubit is sent to another node\n"
                    "- Qubit is measured (with inplace=False)\n"
                    "- Qubit is released\n"
                    "- Qubit is not received\n"
                    "- Qubit is used and created in the same factory\n"
                    "- Qubit is measured (with inplace=False) inside a cqc_if block earlier in the code\n"
                )

    def _set_active(self, be_active):

        # Set the scope of deactivation to the current scope, if inside a CQCMix.
        if not be_active and self._cqc._inside_cqc_mix:
            self.scope_of_deactivation = self._cqc.current_scope

        # Check if not already new state
        if self._active == be_active:
            return

        if be_active:
            self._cqc.active_qubits.append(self)
        else:
            if self in self._cqc.active_qubits:
                self._cqc.active_qubits.remove(self)

        self._active = be_active

    def _single_qubit_gate(self, command, notify, block):
        """
        Performs a single qubit gate specified by the command, called in I(), X(), Y() etc
        :param command: the identifier of the command, as specified in cqcHeader.py
        :param notify: Do we wish to be notified when done
        :param block: Do we want the qubit to be blocked
        """
        # check if qubit is active
        self.check_active()

        if self._cqc.pend_messages:

            self._build_and_pend_command(command, notify, block)

            # print info
            logging.debug(
                "App {} pends message: 'Perform command {} to qubit with ID {}'".format(
                    self._cqc.name, command, self._qID
                )
            )

        else:
            # print info
            logging.debug(
                "App {} tells CQC: 'Send command {} for qubit with ID {}'".format(self._cqc.name, command, self._qID)
            )

            self._cqc.sendCommand(self._qID, command, notify=int(notify), block=int(block))
            if notify:
                message = self._cqc.readMessage()
                self._cqc.print_CQC_msg(message)

    def I(self, notify=True, block=True):
        """
        Performs an identity gate on the qubit.
        If notify, the return message is received before the method finishes.

        - **Arguments**

            :nofify:     Do we wish to be notified when done.
            :block:         Do we want the qubit to be blocked
        """
        self._single_qubit_gate(CQC_CMD_I, notify, block)

    def X(self, notify=True, block=True):
        """
        Performs a X on the qubit.
        If notify, the return message is received before the method finishes.

        - **Arguments**

            :nofify:     Do we wish to be notified when done.
            :block:         Do we want the qubit to be blocked
        """
        self._single_qubit_gate(CQC_CMD_X, notify, block)

    def Y(self, notify=True, block=True):
        """
        Performs a Y on the qubit.
        If notify, the return message is received before the method finishes.

        - **Arguments**

            :nofify:     Do we wish to be notified when done.
            :block:         Do we want the qubit to be blocked
        """
        self._single_qubit_gate(CQC_CMD_Y, notify, block)

    def Z(self, notify=True, block=True):
        """
        Performs a Z on the qubit.
        If notify, the return message is received before the method finishes.

        - **Arguments**

            :nofify:     Do we wish to be notified when done.
            :block:         Do we want the qubit to be blocked
        """
        self._single_qubit_gate(CQC_CMD_Z, notify, block)

    def T(self, notify=True, block=True):
        """
        Performs a T gate on the qubit.
        If notify, the return message is received before the method finishes.

        - **Arguments**

            :nofify:     Do we wish to be notified when done.
            :block:         Do we want the qubit to be blocked
        """
        self._single_qubit_gate(CQC_CMD_T, notify, block)

    def H(self, notify=True, block=True):
        """
        Performs a Hadamard on the qubit.
        If notify, the return message is received before the method finishes.

        - **Arguments**

            :nofify:     Do we wish to be notified when done.
            :block:         Do we want the qubit to be blocked
        """
        self._single_qubit_gate(CQC_CMD_H, notify, block)

    def K(self, notify=True, block=True):
        """
        Performs a K gate on the qubit.
        If notify, the return message is received before the method finishes.

        - **Arguments**

            :nofify:     Do we wish to be notified when done.
            :block:         Do we want the qubit to be blocked
        """
        self._single_qubit_gate(CQC_CMD_K, notify, block)

    def _build_and_pend_command(self, command, notify=False, block=False, subheader: Header = None, *subheader_values):

        # If we are inside a TP_MIX, then insert the CQC Type header before the command header
        if self._cqc._inside_cqc_mix:
            self._cqc._pend_type_header(
                CQCType.COMMAND, 
                CQCCmdHeader.HDR_LENGTH + (subheader.HDR_LENGTH if subheader is not None else 0)
            )

        # Build and pend the command header
        command_header = CQCCmdHeader()
        command_header.setVals(self._qID, command, notify, block)
        self._cqc._pend_header(command_header)

        # Build and pend the subheader, if there is one
        if subheader is not None:
            subheader.setVals(*subheader_values)
            self._cqc._pend_header(subheader)
            
    def _single_gate_rotation(self, command, step, notify, block):
        """
        Perform a rotation on a qubit
        :param command: the rotation qubit command as specified in cqcHeader.py
        :param step: Determines the rotation angle in steps of 2*pi/256
        :param notify: Do we wish to be notified when done
        :param block: Do we want the qubit to be blocked
        :return:
        """
        # check if qubit is active
        self.check_active()

        if self._cqc.pend_messages:

            self._build_and_pend_command(command, notify, block, CQCRotationHeader(), step)
            
            # print info
            logging.debug(
                "App {} pends message: 'Perform rotation command {} (angle {}*2pi/256) to qubit with ID {}'".format(
                    self._cqc.name, command, step, self._qID
                )
            )
        else:
            # print info
            logging.debug(
                "App {} tells CQC: 'Perform rotation command {} (angle {}*2pi/256) to qubit with ID {}'".format(
                    self._cqc.name, command, step, self._qID
                )
            )
            self._cqc.sendCmdXtra(self._qID, command, step=step, notify=int(notify), block=int(block))
            if notify:
                message = self._cqc.readMessage()
                self._cqc.print_CQC_msg(message)

    def rot_X(self, step, notify=True, block=True):
        """
        Applies rotation around the x-axis with the angle of step*2*pi/256 radians.
        If notify, the return message is received before the method finishes.

        - **Arguments**

            :step:         Determines the rotation angle in steps of 2*pi/256
            :nofify:     Do we wish to be notified when done.
            :block:         Do we want the qubit to be blocked
        """
        self._single_gate_rotation(CQC_CMD_ROT_X, step, notify, block)

    def rot_Y(self, step, notify=True, block=True):
        """
        Applies rotation around the y-axis with the angle of step*2*pi/256 radians.
        If notify, the return message is received before the method finishes.

        - **Arguments**

            :step:         Determines the rotation angle in steps of 2*pi/256
            :nofify:     Do we wish to be notified when done.
            :block:         Do we want the qubit to be blocked
        """
        self._single_gate_rotation(CQC_CMD_ROT_Y, step, notify, block)

    def rot_Z(self, step, notify=True, block=True):
        """
        Applies rotation around the z-axis with the angle of step*2*pi/256 radians.
        If notify, the return message is received before the method finishes.

        - **Arguments**

            :step:         Determines the rotation angle in steps of 2*pi/256
            :nofify:     Do we wish to be notified when done.
            :block:         Do we want the qubit to be blocked
        """
        self._single_gate_rotation(CQC_CMD_ROT_Z, step, notify, block)

    def _two_qubit_gate(self, command, target, notify, block):
        """
        Perform a two qubit gate on the qubit
        :param command: the two qubit gate command as specified in cqcHeader.py
        :param target: The target qubit
        :param notify: Do we wish to be notified when done
        :param block: Do we want the qubit to be blocked
        """
        # check if qubit is active
        self.check_active()
        target.check_active()

        if self._cqc != target._cqc:
            raise CQCUnsuppError("Multi qubit operations can only operate on qubits in the same process")

        if self == target:
            raise CQCUnsuppError("Cannot perform multi qubit operation where control and target are the same")

        if self._cqc.pend_messages:

            self._build_and_pend_command(command, notify, block, CQCXtraQubitHeader(), target._qID)

            # print info
            logging.debug(
                "App {} pends message: 'Perform CNOT to qubits with IDs {}(control) {}(target)'".format(
                    self._cqc.name, self._qID, target._qID
                )
            )   
        else:
            # print info
            logging.debug(
                "App {} tells CQC: 'Perform CNOT to qubits with IDs {}(control) {}(target)'".format(
                    self._cqc.name, self._qID, target._qID
                )
            )
            self._cqc.sendCmdXtra(self._qID, command, notify=int(notify), block=int(block), xtra_qID=target._qID)
            if notify:
                message = self._cqc.readMessage()
                self._cqc.print_CQC_msg(message)

    def cnot(self, target, notify=True, block=True):
        """
        Applies a cnot onto target.
        Target should be a qubit-object with the same cqc connection.
        If notify, the return message is received before the method finishes.

        - **Arguments**

            :target:     The target qubit
            :nofify:     Do we wish to be notified when done.
            :block:         Do we want the qubit to be blocked
        """
        self._two_qubit_gate(CQC_CMD_CNOT, target, notify, block)

    def cphase(self, target, notify=True, block=True):
        """
        Applies a cphase onto target.
        Target should be a qubit-object with the same cqc connection.
        If notify, the return message is received before the method finishes.

        - **Arguments**

            :target:     The target qubit
            :nofify:     Do we wish to be notified when done.
            :block:         Do we want the qubit to be blocked
        """
        self._two_qubit_gate(CQC_CMD_CPHASE, target, notify, block)

    def measure(self, inplace=False, block=True):
        """
        Measures the qubit in the standard basis and returns the measurement outcome.
        If now MEASOUT message is received, None is returned.
        If inplace=False, the measurement is destructive and the qubit is removed from memory.
        If inplace=True, the qubit is left in the post-measurement state.

        - **Arguments**

            :inplace:     If false, measure destructively.
            :block:         Do we want the qubit to be blocked
        """
        # check if qubit is active
        self.check_active()

        if inplace:
            command = CQC_CMD_MEASURE_INPLACE
        else:
            command = CQC_CMD_MEASURE
            # Set qubit to non active so the user can receive helpful errors during compile time 
            # if this qubit is used after this measurement
            self._set_active(False)

        if self._cqc.pend_messages:

            # Create a CQC Variable that holds the reference id for the measurement outcome
            cqc_variable = CQCVariable()

            self._build_and_pend_command(command, False, block, CQCAssignHeader(), cqc_variable.ref_id)

            # print info
            logging.debug("App {} pends message: 'Measure qubit with ID {}'".format(self._cqc.name, self._qID))

            return cqc_variable

        else:
            # print info
            logging.debug("App {} tells CQC: 'Measure qubit with ID {}'".format(self._cqc.name, self._qID))

            # Ref id is unimportant in this case because we are not inside a CQCMix
            self._cqc.sendCmdXtra(self._qID, command, notify=0, block=int(block), ref_id=0)

            # Return measurement outcome
            message = self._cqc.readMessage()

            try:
                otherHdr = message[1]
                return otherHdr.outcome
            except AttributeError:
                return None

    def reset(self, notify=True, block=True):
        """
        Resets the qubit.
        If notify, the return message is received before the method finishes.

        - **Arguments**

            :nofify:     Do we wish to be notified when done.
            :block:         Do we want the qubit to be blocked
        """
        # check if qubit is active
        self.check_active()

        if self._cqc.pend_messages:

            self._build_and_pend_command(CQC_CMD_RESET, notify, block)

            # print info
            logging.debug("App {} pends message: 'Reset qubit with ID {}'".format(self._cqc.name, self._qID))
        else:
            # print info
            logging.debug("App {} tells CQC: 'Reset qubit with ID {}'".format(self._cqc.name, self._qID))

            self._cqc.sendCommand(self._qID, CQC_CMD_RESET, notify=int(notify), block=int(block))
            if notify:
                message = self._cqc.readMessage()
                self._cqc.print_CQC_msg(message)

    def release(self, notify=True, block=True):
        """
        Release the current qubit
        :param notify: Do we wish to be notified when done
        :param block: Do we want the qubit to be blocked
        :return:
        """
        return self._cqc.release_qubits([self], notify=notify, block=block)

    def getTime(self, block=True):
        """
        Returns the time information of the qubit.
        If now INF_TIME message is received, None is returned.

        - **Arguments**

            :block:         Do we want the qubit to be blocked
        """
        # check if qubit is active
        self.check_active()

        # print info
        logging.debug("App {} tells CQC: 'Return time-info of qubit with ID {}'".format(self._cqc.name, self._qID))

        self._cqc.sendGetTime(self._qID, notify=0, block=int(block))

        # Return time-stamp
        message = self._cqc.readMessage()
        try:
            otherHdr = message[1]
            return otherHdr.datetime
        except AttributeError:
            return None
