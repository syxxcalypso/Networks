import socket
import sys
import _thread
import time
import string
import packet
import udt
import random
from timer import Timer

# SETTINGS
PACKET_SIZE = 512
RECEIVER_ADDR = ('localhost', 8080)
SENDER_ADDR = ('localhost', 9090)
SLEEP_INTERVAL = 2.0 # (In seconds)
TIMEOUT_INTERVAL = 1.0
WINDOW_SIZE = 4
RETRY_ATTEMPTS = 20

# SHARED RESOURCES
base = 0
pkt_buffer = []
mutex = _thread.allocate_lock()
timer = Timer(TIMEOUT_INTERVAL)

# RELAY CONTROL
threads = 0
sync = False


# Generate random payload of any length
def generate_payload(length=10):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))

    return result_str


# Send using Stop_n_wait protocol
def send_snw(sock):

    # Access to shared resources
    global threads, sync

    # Put name in hat
    threads += 1

    # Track packet count
    seq = 0

    # Open local stream
    with open(filename, "r") as f:

        # Do-While Trick
        data = True

        # Sequential File Access
        while data:

            # Lock Context
            with mutex:

                # Debugging Info
                print("1 - Acquired w/ {}".format(seq+1))

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

    # Remove name from hat
    threads -= 1

# Send using GBN protocol
def send_gbn(sock):

    return

# Receive thread for stop-n-wait
def receive_snw(sock, pkt):

    # Shared Resource Access
    global threads, sync

    # Put Name in Hat
    threads += 1

    # Spin lock to synchronize execution
    while not sync:
        continue

    # While Packets still exist
    while pkt_buffer:

        # Manually lock
        mutex.acquire()

        # Debugging info
        print("2 - Acquired")

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
    threads -= 1
   


# Receive thread for GBN
def receive_gbn(sock):
    # Fill here to handle acks
    return


# Main function
if __name__ == '__main__':
    #if len(sys.argv) != 2:
    #    print('Expected filename as command line argument')
    #    exit()


    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(0)
    sock.bind(SENDER_ADDR)

    #filename = sys.argv[1]
    filename = "/home/shor/meta"

    print("pre")

    base = 0

    _thread.start_new_thread(send_snw, (sock,))
    time.sleep(1)
    _thread.start_new_thread(receive_snw, (sock, pkt_buffer))

    while threads:
        continue

    print("post")
    sock.close()


