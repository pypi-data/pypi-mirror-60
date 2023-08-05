portwait
=========

CLI Tool for waiting on ports to open.


# Usage

    usage: portwait [-h] [-t TIMEOUT] [-v] host port

    positional arguments:
      host                  Host to connect to
      port                  ... its the port ok?

    optional arguments:
      -h, --help            show this help message and exit
      -t TIMEOUT, --timeout TIMEOUT
                            Timeout in seconds
      -v, --verbose         Describe result


# Example

Wait for ssh to open up (presumably after a reboot or something):

    portwait 10.40.1.100 22

Do a single check and don't wait

    portwait 10.40.1.100 22 --timeout 0
