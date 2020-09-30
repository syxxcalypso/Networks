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
SLEEP_INTERVAL = 1.0 # (In seconds)
TIMEOUT_INTERVAL = 0.5
WINDOW_SIZE = 4

# You can use some shared resources over the two threads
base = 0
window = []
mutex = _thread.allocate_lock()
timer = Timer(TIMEOUT_INTERVAL)

# Relay control
threads = 0
sync = False

# Need to have two threads: one for sending and another for receiving ACKs

# Generate random payload of any length
def generate_payload(length=10):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))

    return result_str


# Send using Stop_n_wait protocol
def send_snw(sock):
    global threads, sync
    threads += 1
    seq = 0
    with open(filename, "r") as f:                    # Open fd
        data = True                                       # do-while trick
        while data:                                       # Data still in stream
            with mutex:
                sync = True
                print("1 - Acquired w/ {seq+1}")
                data = f.read(PACKET_SIZE).encode()             # Read stream
                pkt = packet.make(seq, data)     # Fill window buffer
                window.append(pkt)
                udt.send(pkt, sock, RECEIVER_ADDR) # Send
                seq += 1                                  # Next
            time.sleep(SLEEP_INTERVAL)              # Give time before ACK check
        pkt = packet.make(seq, "END".encode())            # Prepare last packet
        udt.send(pkt, sock, RECEIVER_ADDR)                # Send EOF
    threads -= 1

# Send using GBN protocol
def send_gbn(sock):

    return

# Receive thread for stop-n-wait
def receive_snw(sock, pkt):
    global threads, sync
    threads += 1
    while not sync:
        continue
    while window:                 # Check packet buffer
        mutex.acquire()
        print("2 - Acquired")
        timer.start()         # Countdown
        p = pkt.pop()         # Pull from buffer
        while True:           # Until ACK
            try:
                #sock.setblocking(True)
                ack, recvaddr = udt.recv(sock) # Check ACK
                timer.stop()
                mutex.release()
                time.sleep(1)
                break
            except BlockingIOError:                    # No ACK
                if timer.timeout():                    # Check timer
                    udt.send(p, sock, RECEIVER_ADDR)   # Resend
                    timer.start()                          # Reset
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
    _thread.start_new_thread(receive_snw, (sock, window))

    while threads:
        continue

    print("post")
    sock.close()


