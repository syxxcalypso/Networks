# receiver.py - The receiver in the reliable data transer protocol
import packet
import socket
import sys
import udt

RECEIVER_ADDR = ('localhost', 8080)

# Receive packets from the sender w/ GBN protocol
def receive_gbn(sock):
    # Fill here
    return


# Receive packets from the sender w/ SR protocol
def receive_sr(sock, windowsize):
    # Fill here
    return


# Receive packets from the sender w/ Stop-n-wait protocol
def receive_snw(sock):

    # Terminal String
    endStr = ''

    # Most recent sequence number
    _seq = -1

    # Blocking Loop
    while True:

        # Block on socket data
        pkt, senderaddr = udt.recv(sock)
        seq, data = packet.extract(pkt)

        # If data is newer
        if _seq != seq:

            # Update last sequence
            _seq = seq

            # Parse data and write debugging info to logging stream
            endStr = data.decode()
            sys.stderr.write("From: {}, Seq# {}\n".format(senderaddr, seq))
            sys.stderr.flush()

            # If string is terminal
            if endStr == 'END':
                return

            # Write socket data to output stream
            sys.stdout.write(endStr)
            sys.stdout.flush()

        # Send null ACK
        udt.send(b' ', sock, ('localhost', 9090))



# Main function
if __name__ == '__main__':
    # if len(sys.argv) != 2:
    #     print('Expected filename as command line argument')
    #     exit()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(RECEIVER_ADDR)
    # filename = sys.argv[1]
    receive_snw(sock)

    # Close the socket
    sock.close()
