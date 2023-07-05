import os
from pathlib import Path

DATA_PATH = Path.home() / ".green-element"
ORDER_FOR_EXPRESS_PATH = f"{DATA_PATH}/order_for_express.xlsx"
DB_PATH = f"{DATA_PATH}/rfid_wms.db"
LICENSE_PATH = f"{DATA_PATH}/license.txt"
DOWNLOAD_PATH = str(DATA_PATH)
LOG_PATH = f"{DATA_PATH}/app.log"