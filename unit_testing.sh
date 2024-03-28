cp ./src/logging.conf logging.conf
pytest
rm -rf logging.conf
rm -rf *.log