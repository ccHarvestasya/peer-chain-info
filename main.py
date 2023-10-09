import os
import sys
import socket
import ssl
from pathlib import Path
from symbolchain.BufferReader import BufferReader
from symbolchain.BufferWriter import BufferWriter

CERTIFICATE_DIRECTORY = os.getcwd() + "\cert"


class ChainStatistics:
    def __init__(self):
        self.height = 0
        self.finalized_height = 0
        self.score_high = 0
        self.score_low = 0

    def __str__(self):
        score = self.score_high << 64 | self.score_low
        return "\n".join(
            [
                f"          height: {self.height}",
                f"finalized height: {self.finalized_height}",
                f"           score: {score}",
            ]
        )


class SymbolPeerClient:
    def __init__(self, host, port, certificate_directory):
        (self.node_host, self.node_port) = (host, port)
        self.certificate_directory = Path(certificate_directory)
        self.timeout = 10

        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        self.ssl_context.load_cert_chain(
            self.certificate_directory / "node.full.crt.pem",
            keyfile=self.certificate_directory / "node.key.pem",
        )

    def _send_socket_request(self, packet_type, parser):
        try:
            with socket.create_connection(
                (self.node_host, self.node_port), self.timeout
            ) as sock:
                with self.ssl_context.wrap_socket(sock) as ssock:
                    self._send_simple_request(ssock, packet_type)
                    return parser(self._read_packet_data(ssock, packet_type))
        except socket.timeout as ex:
            raise ConnectionRefusedError from ex

    @staticmethod
    def _send_simple_request(ssock, packet_type):
        writer = BufferWriter()
        writer.write_int(8, 4)
        writer.write_int(packet_type, 4)
        ssock.send(writer.buffer)

    def _read_packet_data(self, ssock, packet_type):
        read_buffer = ssock.read()

        if 0 == len(read_buffer):
            raise ConnectionRefusedError(
                f"socket returned empty data for {self.node_host}"
            )

        size = BufferReader(read_buffer).read_int(4)

        while len(read_buffer) < size:
            read_buffer += ssock.read()

        reader = BufferReader(read_buffer)
        size = reader.read_int(4)
        actual_packet_type = reader.read_int(4)

        if packet_type != actual_packet_type:
            raise ConnectionRefusedError(
                f"socket returned packet type {actual_packet_type} but expected {packet_type}"
            )

        return reader

    def get_chain_statistics(self):
        packet_type = 5
        return self._send_socket_request(
            packet_type, self._parse_chain_statistics_response
        )

    @staticmethod
    def _parse_chain_statistics_response(reader):
        chain_statistics = ChainStatistics()

        chain_statistics.height = reader.read_int(8)
        chain_statistics.finalized_height = reader.read_int(8)
        chain_statistics.score_high = reader.read_int(8)
        chain_statistics.score_low = reader.read_int(8)

        return chain_statistics


def main(argv):
    port = 7900
    if 0 == len(argv):
        print("Arguments are too short")
        return 1
    elif 3 <= len(argv):
        if not argv[2].isdigit():
            print("Argument is not digit")
            return 1
        port = argv[2]

    peer_client = SymbolPeerClient(argv[1], port, CERTIFICATE_DIRECTORY)
    chain_statistics_peer = peer_client.get_chain_statistics()
    print(chain_statistics_peer)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
