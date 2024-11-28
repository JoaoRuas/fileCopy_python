"""
Creates a copy of a folder and keeps the replica updated
The copying systems only works one way (original ==> replica)
"""

import os
import shutil
import threading
import time
import sys
from datetime import datetime

# List all of the files from the folder in the provided location
def lookup_all_files(path : str) -> list:
    """
    Walks through the directory tree starting at the given path and
      returns a list of all files encountered.
    
    Args:
        path (str): The path to the root of the directory tree to be traversed.
    
    Returns:
        list: A list of all files found in the directory tree.
    """
    files_list = []
    for root, _, files in os.walk(path, topdown=False):
        for name in files:
            files_list.append(os.path.join(root, name))
    return files_list

# Compares files from each list for differences
# Creates missing files, updates outdated files and
#   deletes the extra in the replica folder
# Logs the changes to the file in log_file_path
def update_files(source_folder : str, source : list,
                 replica_folder :str, replica : list,
                 log_file_path: str):
    """
    Compares files from each list for differences
    Creates missing files, updates outdated files and deletes the extra in the replica folder
    Logs the changes to the file in log_file_path
    
    Args:
        source_folder (str): The path to the folder containing the source files
        source (list): A list of all files in the source folder
        replica_folder (str): The path to the folder containing the replica files
        replica (list): A list of all files in the replica folder
        log_file_path (str): The path to the file where changes are logged
    """
    with open(log_file_path, 'a') as log_file:
        for file in source:
            replica_file = file.replace(source_folder, replica_folder)
            if replica_file in replica:
                i = replica.index(replica_file)
                if os.path.getmtime(file) != os.path.getmtime(replica[i]):
                    shutil.copy2(file, replica[i])
                    message = f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] {file} was updated'
                    log_file.write(message + '\n')
                    print(message)
                replica.pop(i)
            else:
                new_file = file.replace(source_folder, replica_folder)
                os.makedirs(os.path.dirname(new_file), exist_ok=True)
                shutil.copy2(file, new_file)
                message = f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] {file} was created'
                log_file.write(message + '\n')
                print(message)

    for file in replica:
        os.remove(file)
        message = f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] {file} was removed'
        log_file.write(message + '\n')
        print(message)

# Creates a timer to run every [interval_duration] seconds and call the update_files function
def func_timer(timer, interval_duration):
    """
    Runs every [interval_duration] seconds and calls the update_files function
    with the current state of the source and replica folders.

    Args:
        timer (threading.Event): A threading event which controls the
            execution of the thread.
        interval_duration (int): The time interval in seconds to wait between
            consecutive executions of the update_files function.
    """
    while timer.is_set():
        source_files = lookup_all_files(in_source_folder)
        replica_files = lookup_all_files(in_replica_folder)

        update_files(in_source_folder, source_files, in_replica_folder, replica_files, in_log_file)

        time.sleep(interval_duration)

if __name__ == "__main__":
# Sets the values from the command line arguments
    in_source_folder = sys.argv[1]
    in_replica_folder = sys.argv[2]
    in_interval_duration = int(sys.argv[3])
    in_log_file = sys.argv[4]

    # Runs the thread with the timer
    timer_runs = threading.Event()
    timer_runs.set()
    t = threading.Thread(target=func_timer, args=(timer_runs, in_interval_duration))
    t.start()
    stop = input('(Press enter to stop after the next check)')
    timer_runs.clear()
