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
    endStr = ''
    _seq = -1
    while True:
        pkt, senderaddr = udt.recv(sock)
        seq, data = packet.extract(pkt)
        if _seq != seq:
            _seq = seq
            endStr = data.decode()
            sys.stderr.write("From: {}, Seq# {}\n".format(senderaddr, seq))
            sys.stderr.flush()
            if endStr == 'END':
                return
            sys.stdout.write(endStr)
            sys.stdout.flush()
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
