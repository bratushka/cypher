#!/usr/bin/env python
import socket
import subprocess
import time


# Wait for the database to be available.
while True:
    try:
        socket.create_connection(('cypher-db', 7687))
        break
    except ConnectionRefusedError:
        time.sleep(1)

# Run the dev server.
subprocess.run(
    ['sh'],
    stderr=subprocess.STDOUT,
)
