copy .\src\logging.conf logging.conf
pytest
del logging.conf
del *.log