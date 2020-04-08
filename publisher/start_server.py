from publisher_server import PublisherServer
import time
import os

def main():
    svr = PublisherServer()

    print(f"Netconf server listening on port {svr.port}")
    try:
        while True:
            time.sleep(200)
    except KeyboardInterrupt:
        print("Server killed")


if __name__ == "__main__":
    main()
