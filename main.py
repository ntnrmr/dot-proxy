#!/usr/bin/python3
"""
DNS to DNS over TLS proxy
"""

import socket
import logging
import threading
import argparse
import ssl
import yaml

MAX_BYTES = 1024
CONFIG_ENCODING = "utf-8"


class DNSProxy:
    """Class represents DNS to DNS over TLS proxy"""

    def __init__(self, cfg):
        self.address = cfg["address"]
        self.port = cfg["port"]
        self.dot_server_address = cfg["dot_server_address"]
        self.dot_server_port = cfg["dot_server_port"]
        self.dot_timeout = cfg["dot_timeout"]

    def query_dot(self, query):
        """Query DoT server and return response
        Args:
            query(bytes): DNS query from client
        Returns:
            response(bytes): Response from DoT
        """
        try:
            ssl_context = ssl.create_default_context()
            with socket.create_connection(
                (self.dot_server_address, self.dot_server_port),
                timeout=self.dot_timeout,
            ) as dns_socket:
                with ssl_context.wrap_socket(
                    dns_socket, server_hostname=self.dot_server_address
                ) as tls_socket:
                    tls_socket.sendall(query)
                    response = tls_socket.recv(MAX_BYTES)
        except socket.timeout:
            logging.error("Timeout: Unable to connect to the DNS over TLS server.")
        except (ssl.SSLError, OSError) as exp:
            logging.error("Error while querying DoT: %s", exp)
        return response

    def handle_client(self, client_socket):
        """Get request from client, forward it to DoT server, return response to client
        Args:
            client_socket (bytes): Connected Client Socket
        """
        client_query = client_socket.recv(MAX_BYTES)
        try:
            response = self.query_dot(client_query)
            if response:
                logging.info("Received DNS response from DoT server")
                client_socket.sendall(response)
                client_socket.close()
                logging.info("Sent DNS response to client socket")
            else:
                logging.error("Failed to get DNS response.")
        except Exception as ex:
            logging.error("Error handling DNS query: %s", ex)

    def run(self):
        """Main loop for accepting connections and serving DNS proxy"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.address, self.port))
        s.listen(5)  # max 5 connections
        logging.info(
            "Started DNS to DNS over TLS proxy on  %s:%s", self.address, self.port
        )
        while True:
            client_socket, client_address = s.accept()
            logging.info(
                "Accepted connection from %s:%s", client_address[0], client_address[1]
            )
            thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            thread.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DNS to DNS over TLS proxy")
    parser.add_argument(
        "--config", type=str, help="Config file", default="./config.yaml"
    )
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    )
    logging.info("Loading config file at %s", args.config)
    try:
        with open(args.config, "r", encoding=CONFIG_ENCODING) as config_file:
            config = yaml.safe_load(config_file)
            if config is None or not isinstance(config, dict):
                raise TypeError("Invalid config file format.")
    except FileNotFoundError as e:
        logging.error("Can't open config file: %s", e)
    except yaml.YAMLError as e:
        logging.error("Error parsing config file: %s", e)
    else:
        proxy = DNSProxy(config)
        proxy.run()
