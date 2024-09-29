import socketio
import subprocess
import requests
import os
import sys

requests.packages.urllib3.disable_warnings()
http_session = requests.Session()
http_session.verify = False
sio = socketio.Client(http_session=http_session)


@sio.event
def connect():
    print("Connection established")
    sio.emit('read_queue', {'queue': os.environ['NOTIFICATION_QUEUE']})


@sio.event
def new_message(data):
    print(f"New message received: {data}")

    if data.startswith("xdg-open"):
        link(data)
    else:
        if data.startswith("!"):
            urgency = 'critical'
        elif data.startswith("Meeting"):
            urgency = 'critical'
        else:
            urgency = 'normal'

        notify(data, urgency)


@sio.event
def wait_message(queue):
    sio.emit('read_queue', {'queue': os.environ['NOTIFICATION_QUEUE']})


@sio.event
def disconnect():
    print("Disconnected from the WebSocket server")


def notify(message, urgency='normal'):
    subprocess.run(['notify-send', os.environ['NOTIFICATION_QUEUE'], message, '-u', urgency])


def link(link):
    parts = link.split()
    subprocess.run(['xdg-open', parts[1]])


def main():
    if 'NOTIFICATION_PASSWORD' not in os.environ:
        print('Missing NOTIFICATION_PASSWORD env var')
        sys.exit(1)

    if 'NOTIFICATION_SERVER' not in os.environ:
        print('Missing NOTIFICATION_SERVER env var')
        sys.exit(1)

    if 'NOTIFICATION_QUEUE' not in os.environ:
        print('Missing NOTIFICATION_QUEUE env var')
        sys.exit(1)

    headers = {
        'X-Auth-Token': os.environ['NOTIFICATION_PASSWORD'],
    }

    # Connect to the server
    sio.connect(os.environ['NOTIFICATION_SERVER'], headers=headers)
    sio.wait()


if __name__ == "__main__":
    main()
