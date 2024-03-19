"""Signal handling utilities.

signal_control
=========
Module that contains logic for signal control.

Classes
-------

BetterSignalHandler
    Class used to set given control flags when specific interrupt occurs.

"""
import signal


class BetterSignalHandler:
    """Class used to set given control flags when specific interrupt occurs.

    This is one time use only signal handler.

    Attributes
    ----------
    sig:
       Signal that is monitored.
    flags:
       Application control flags that will be set when signal is received.
    original_handler:
       Original handler for this signal so that it can be reassigned.

    Methods
    -------
    handler:
       Handler that is executed on received signal.

    """

    def __init__(self, sig, flags):
        """Create signal handler.

        Parameters
        ----------
        sig:
           Signal to be monitored.
        flags:
           Control flags to be set on received signal.
        """
        self.sig = sig
        self.flags = flags
        self.original_handler = signal.getsignal(self.sig)
        signal.signal(self.sig, self.handler)

    def handler(self, signum, frame):
        """Handle signal.

        Parameters
        ----------
        signum:
           Signal to be monitored.
        frame:
        """
        for flag in self.flags:
            flag.set()
        signal.signal(self.sig, self.original_handler)
