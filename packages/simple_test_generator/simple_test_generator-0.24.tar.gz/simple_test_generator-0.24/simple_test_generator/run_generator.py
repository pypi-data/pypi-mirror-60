import select
import threading
from collections import deque

from botostubs.pythonic import Hey

from simple_test_generator import Recorder


def hey():
    print('hey')


def consume_socket_content(sock, timeout=0.5):
    chunks = 65536
    content = b''

    while True:
        more_to_read = select.select([sock], [], [], timeout)[0]
        if not more_to_read:
            break

        new_content = sock.recv(chunks)
        if not new_content:
            break

        content += new_content

    return content


def main():
    Hey.text_response_server('hi')
    with Recorder():
        # Hey(1).start()
        close_server = threading.Event()
        Hey.basic_response_server(wait_to_close_event=close_server)
        Hey(1).go_instance()
        # hey()
        Hey.basic_response_server()
        Hey.text_response_server('hey')


if __name__ == '__main__':
    main()
