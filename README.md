USAGE
=====

sender usage: ./sender.py [-h] <input file name> <protocol>
receiver usage: ./receuver.py [-h] <protocol>

where <protocol> is either 'snw' or 'gbn'
and <input file name> is an OS compliant path name to the file stream

Logging for sender occurs on stdout

Logging for receiver occurs on stderr, data output is sent to stdout

EXAMPLE
=======

To write to file "MyFile.txt" using Go-Back-N:

./receiver.py gbn > MyFile.txt
./sender.pt gbn

This allows for debugging info on the terminal while executing
