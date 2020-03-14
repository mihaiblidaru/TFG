from publisher_server import PublisherServer
import time


def main():
    svr = PublisherServer("admin", "admin")

    print(f"Netconf server listening on port {svr.port}")
    try:
        while True:
            time.sleep(200)
    except KeyboardInterrupt:
        print("Server killed")


if __name__ == "__main__":
    main()
