from publisher_server import PublisherServer
import time
import os
from argparse import ArgumentParser

class Parser(ArgumentParser):
    help_str = """Netconf Server with yang pusn notification capabilities."""

    def __init__(self, prog):
        super().__init__(prog, description=self.help_str)

        self.add_argument('-c', '--conf', required=False, default="server_config.json", help='Netconf server config file'),

    def parse_argv(self):
        return vars(self.parse_args())


def main():

    parser = Parser(__file__)
    args = parser.parse_args()

    svr = PublisherServer(args.conf)

    print(f"Netconf server listening on port {svr.port}")
    try:
        while True:
            time.sleep(200)
    except KeyboardInterrupt:
        print("Server killed")


if __name__ == "__main__":
    main()
