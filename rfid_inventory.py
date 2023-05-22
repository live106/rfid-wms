import time
import threading
from rfid_api import async_get_epc_list, stop_async_inventory_event

def start_async_inventory(counter_thread, rfid_thread, epc_list, inventory_duration_ref):
    stop_async_inventory_event.clear()
    if not counter_thread.is_alive():
        counter_thread = threading.Thread(target=update_counter_thread, args=(epc_list, inventory_duration_ref))
    if not rfid_thread.is_alive():
        rfid_thread = threading.Thread(target=get_epc_list_thread, args=(epc_list, inventory_duration_ref))
    counter_thread.start()
    rfid_thread.start()

def stop_async_inventory(counter_thread, epc_list, inventory_duration_ref):
    stop_async_inventory_event.set()
    counter_thread.join()
    quantity = len(epc_list)
    epc_list.clear()
    inventory_duration_ref[0] = 0
    return quantity

def update_counter_thread(epc_list, inventory_duration_ref):
    while not stop_async_inventory_event.is_set():
        try:
            time.sleep(1)
            count = len(epc_list)
            inventory_duration_ref[0] += 1
            print(f"Counter updated: {count}, inventory_duration_ref: {inventory_duration_ref[0]}")
        except Exception as e:
            error_message = str(e)
            print(error_message)
            pass
    print("Counter updated done.")

def get_epc_list_thread(epc_list, inventory_duration_ref):
    async_get_epc_list(epc_list, inventory_duration_ref)
    stop_async_inventory()