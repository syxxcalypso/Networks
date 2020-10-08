USAGE
=====

sender usage: ./sender.py [-h] <protocol>
receiver usage: ./receuver.py [-h] <protocol>

where <protocol> is either 'snw' or 'gbn'


Logging for sender occurs on stdout

Logging for receiver occurs on stderr, data output is sent to stdout

EXAMPLE
=======

To write to file "MyFile.txt" using Go-Back-N:

./receiver.py gbn > MyFile.txt
./sender.pt gbn

This allows for debugging info on the terminal while executing
