from src import Exporter
from dotenv import load_dotenv
import os
load_dotenv()

MODEM_HOSTNAME = os.getenv('MODEM_HOSTNAME')
MODEM_USERNAME = os.getenv('MODEM_USERNAME')
MODEM_PASSWORD = os.getenv('MODEM_PASSWORD')
EXPORTER_PORT = os.getenv('EXPORTER_PORT')
exporter = Exporter(MODEM_HOSTNAME, MODEM_USERNAME, MODEM_PASSWORD, EXPORTER_PORT)
exporter.schedule_jobs()
