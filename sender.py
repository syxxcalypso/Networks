#!/usr/bin/env python3
import socket
import sys
import _thread
import time
import string
import packet
import udt
import random
import argparse
from timer import Timer

# SETTINGS
PACKET_SIZE = 512
RECEIVER_ADDR = ('localhost', 8080)
SENDER_ADDR = ('localhost', 9090)
SLEEP_INTERVAL = 1.0 # (In seconds)
TIMEOUT_INTERVAL = 1.0
WINDOW_SIZE = 4
RETRY_ATTEMPTS = 24

# SHARED RESOURCES
base = 0
data = True
pkt_buffer = []
mutex = _thread.allocate_lock()
timer = Timer(TIMEOUT_INTERVAL)

# RELAY CONTROL
sync = False
alive = True

# Generate random payload of any length
def generate_payload(length=10):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))

    return result_str


# Send using Stop_n_wait protocol
def send_snw(sock):

    # Access to shared resources
    global sync, data

    # Track packet count
    seq = 0

    # Open local stream
    with open(filename, "r") as f:

        # Sequential File Access
        while data:

            # Lock Context
            with mutex:

                # Debugging Info
                print("[I] SEND - Acquired Lock")

                # Generate Packet & Link Buffer
                data = f.read(PACKET_SIZE).encode()
                pkt = packet.make(seq, data)
                pkt_buffer.append(pkt)

                # Handle Thread Timing
                sync = True

                # Send Packet and Increment Sequence
                udt.send(pkt, sock, RECEIVER_ADDR)
                seq += 1

            # Delay Mutex for sister thread
            time.sleep(SLEEP_INTERVAL)

        # Prepare & Send END packet
        with mutex:
            pkt = packet.make(seq, "END".encode())            # Prepare last packet
            pkt_buffer.append(pkt)
            udt.send(pkt, sock, RECEIVER_ADDR)                # Send EOF

# Send using GBN protocol
def send_gbn(sock):
    # Access to shared resources
    global sync, data

    # Track packet count
    seq = 0

    # Set data proper
    data = []

    # Open local stream
    with open(filename, "r") as f:

        print("[I] SEND - Initial Stream")

        for i in range(WINDOW_SIZE):
            data = f.read(PACKET_SIZE).encode()
            if data:
                print("[I] SEND - Pushing to Buffer Pkt# {}".format(seq))
                pkt = packet.make(seq, data)
                pkt_buffer.append((pkt, seq))
                seq += 1


        _base = 0

        # Sequential File Access
        while data or pkt_buffer:


            # Bound by window
            while pkt_buffer:
                # Delay Mutex for sister thread
                time.sleep(SLEEP_INTERVAL)

                with mutex:

                    sync = True

                    print("\n[I] SEND - Acquired Lock")
                    for pkt in pkt_buffer:
                        print("[I] SEND - Sending Pkt# {}".format(pkt[1]))
                        udt.send(pkt[0], sock, RECEIVER_ADDR)


            for i in range(base - _base):
                data = f.read(PACKET_SIZE).encode()
                if data:
                    pkt = packet.make(seq, data_)
                    pkt_buffer.append((pkt, seq))
                    seq += 1
            _base = base

    # Prepare & Send END packet
    with mutex:
        pkt = packet.make(seq, "END".encode())            # Prepare last packet
        pkt_buffer.append(pkt)
        udt.send(pkt, sock, RECEIVER_ADDR)                # Send EOF

    print("[I] SEND - Terminating Thread, Buffer Size: {}".format(len(pkt_buffer)))
    alive = False
    return

# Receive thread for stop-n-wait
def receive_snw(sock, pkt):

    # Shared Resource Access
    global sync, alive

    # Spin lock to synchronize execution
    while not sync:
        continue

    # While Packets still exist
    while pkt_buffer:

        # Manually lock
        mutex.acquire()

        # Debugging info
        print("[I] RECV - Acquired Lock")

        # Retry Delay
        timer.start()

        # Get Packet
        p = pkt.pop()

        # R
        retry = RETRY_ATTEMPTS
        while retry:
            try:
                # Try ACK Check
                ack, recvaddr = udt.recv(sock)

                # If received, cleanup and pass baton
                timer.stop()
                mutex.release()
                time.sleep(SLEEP_INTERVAL)
                retry = RETRY_ATTEMPTS
                break

            except BlockingIOError:

                # Otherwise, check timer and restart
                if timer.timeout():
                    retry -= 1
                    udt.send(p, sock, RECEIVER_ADDR)
                    timer.start()

    # Remove name from hat
    alive = False

    # Mutex is held on purpose to ensure
    # Data misordering at fail doesn't occur


# Receive thread for GBN
def receive_gbn(sock):

    # Shared Resource Access
    global sync, alive, base, data

    # Spin lock to synchronize execution
    while not sync:
        continue

    retry = RETRY_ATTEMPTS

    base = 0

    # Retry Delay
    timer.start()

    # Retry Loop
    while retry and (pkt_buffer or alive):

        bad_seq_or_broken = False

        try:
            # Try ACK Check
            ack, recvaddr = udt.recv(sock)
            seq, ack_data = packet.extract(ack)

            with mutex:

                print("\n[I] RECV - Acquired Lock")

                # Check for base packet reception
                if seq == base:

                    print("[I] RECV - Got ACK Seq# {}".format(seq))

                    #sys.stderr.write("ACK on Seq# {}\n".format(seq))
                    #sys.stderr.flush()

                    base += 1
                    pkt_buffer.pop(0)
                    timer.stop()
                    retry = RETRY_ATTEMPTS
                    continue

            bad_seq_or_broken = True

            print("[W] RECV - Got Wrong ACK Seq# {}, Expected {}".format(seq, base))

        except BlockingIOError:

            bad_seq_or_broken = True

        # Otherwise, check timer and restart
        if timer.timeout() and bad_seq_or_broken:
            retry -= 1
            timer.start()

    # Mutex is held on purpose to ensure
    # Data misordering at fail doesn't occur

    print("[I] RECV - Terminating Thread")
    return

def parse_args():
    parser = argparse.ArgumentParser(description='Receive UDP packets.')
    parser.add_argument('method', metavar='<protocol>', type=str,
                        help='Phrase length(s)')
    return parser.parse_args()

# Main function
if __name__ == '__main__':

    args = parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(0)
    sock.bind(SENDER_ADDR)

    filename = sys.argv[1]
    #filename = "/home/shor/meta"

    print("pre")

    base = 0

    if args.method == 'snw':
        _thread.start_new_thread(send_snw, (sock,))
        time.sleep(1)
        _thread.start_new_thread(receive_snw, (sock,))
    elif args.method == 'gbn':
        _thread.start_new_thread(send_gbn, (sock,))
        time.sleep(1)
        _thread.start_new_thread(receive_gbn, (sock,))
    else:
        sys.stderr.write("Protocol selection must be one of [\'snw\', \'gbn\']\n")
        sys.stderr.flush()

    # problem with alive and sync on recv
    while alive:
        continue

    print("post")
    sock.close()


