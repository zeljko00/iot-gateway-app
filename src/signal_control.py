"""Signal handling utilities.

signal_control
=========
Module that contains logic for signal control.

Classes
-------

BetterSignalHandler
    Class used to set given control flags when specific signals are received.

"""
import signal


class BetterSignalHandler:
    """Class used to set given control flags when specific interrupt occurs.

    This is one time use only signal handler.

    Attributes
    ----------
    sigs:
       Signals that is monitored.
    flags:
       Application control flags that will be set when signal is received.
    original_handlers:
       Original handlers for all chosen signals.

    Methods
    -------
    handler:
       Handler that is executed on received signal.

    """

    def __init__(self, sigs, flags):
        """Create signal handler.

        Parameters
        ----------
        sigs:
           Signals to be monitored.
        flags:
           Control flags to be set on received signal.
        """
        self.sigs = sigs
        self.flags = flags
        self.original_handlers = []
        for sig in self.sigs:
            self.original_handlers.append(signal.getsignal(sig))
            signal.signal(sig, self.handler)

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
        for sig, original_handler in zip(self.sigs, self.original_handlers):
            signal.signal(sig, original_handler)
