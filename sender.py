import socket
import sys
import _thread
import time
import string
import packet
import udt
import random
from timer import Timer

# Some already defined parameters
PACKET_SIZE = 512
RECEIVER_ADDR = ('localhost', 8080)
SENDER_ADDR = ('localhost', 9090)
SLEEP_INTERVAL = 0.05 # (In seconds)
TIMEOUT_INTERVAL = 0.5
WINDOW_SIZE = 4

# You can use some shared resources over the two threads
base = 0
window = [packet.make(-1, "END".encode())]
mutex = _thread.allocate_lock()
timer = Timer(TIMEOUT_INTERVAL)

# Need to have two threads: one for sending and another for receiving ACKs

# Generate random payload of any length
def generate_payload(length=10):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))

    return result_str


# Send using Stop_n_wait protocol
def send_snw(sock):
    seq = 0
    with open(filename, "rb") as file:                    # Open fd
        data = True                                       # do-while trick
        while data:                                       # Data still in stream
            with mutex:                                   # Block
                data = file.read(PACKET_SIZE)             # Read stream
                window.append(packet.make(seq, data))     # Fill window buffer
                udt.send(window[-1], sock, RECEIVER_ADDR) # Send
                seq += 1                                  # Next
                time.sleep(TIMEOUT_INTERVAL)              # Give time before ACK check
        pkt = packet.make(seq, "END".encode())            # Prepare last packet
        udt.send(pkt, sock, RECEIVER_ADDR)                # Send EOF

# Send using GBN protocol
def send_gbn(sock):

    return

# Receive thread for stop-n-wait
def receive_snw(sock, pkt):
    while window:                 # Check packet buffer
        with mutex:               # Block
            timer.start()         # Countdown
            p = pkt.pop()         # Pull from buffer
            while True:           # Until ACK
                try:
                    ack, recvaddr = udt.recv(sock) # Check ACK
                    break
                except BlockingIOError:                    # No ACK
                    if timer.timeout():                    # Check timer
                        udt.send(p, sock, RECEIVER_ADDR)   # Resend
                        t.start()                          # Reset
   


# Receive thread for GBN
def receive_gbn(sock):
    # Fill here to handle acks
    return


# Main function
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Expected filename as command line argument')
        exit()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(0)
    sock.bind(SENDER_ADDR)

    filename = sys.argv[1]
    _thread.start_new_thread(send_)

    sock.close()


