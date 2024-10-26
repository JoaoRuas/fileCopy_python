import os, shutil, threading, time, sys
from datetime import datetime

# List all of the files from the folder in the provided location
def lookupAllFiles(path : str) -> list:
  filesList = []
  for root, _, files in os.walk(path, topdown=False):
    for name in files:
      filesList.append(os.path.join(root, name))
  return filesList

# Compares files from each list for differences
# Creates missing files, updates outdated files and deletes the extra in the replica folder
# Logs the changes to the file in logFilePath
def updateFiles(sourceFolder : str, source : list, replicaFolder :str, replica : list, logFilePath: str):
  logFile = open(logFilePath, 'a')
  for file in source:
    replicaFile = file.replace(sourceFolder, replicaFolder)
    if(replicaFile in replica):
      i = replica.index(replicaFile)
      if(os.path.getmtime(file) != os.path.getmtime(replica[i])):
        shutil.copy2(file, replica[i])
        message = f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] {file} was updated'
        logFile.write(message + '\n')
        print(message)
      replica.pop(i)
    else:
      newFile = file.replace(sourceFolder, replicaFolder)
      os.makedirs(os.path.dirname(newFile), exist_ok=True)
      shutil.copy2(file, newFile)
      message = f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] {file} was created'
      logFile.write(message + '\n')
      print(message)

  for file in replica:
    os.remove(file)
    message = f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] {file} was removed'
    logFile.write(message + '\n')
    print(message)

# Creates a timer to run every [intervalDuration] seconds and call the updateFiles function
def timer(timer_runs, intervalDuration):
    while timer_runs.is_set():
        sourceFiles = lookupAllFiles(sourceFolder)
        replicaFiles = lookupAllFiles(replicaFolder)

        updateFiles(sourceFolder, sourceFiles, replicaFolder, replicaFiles, logFile)

        time.sleep(intervalDuration)

# Sets the values from the command line arguments
sourceFolder = sys.argv[1]
replicaFolder = sys.argv[2]
intervalDuration = int(sys.argv[3])
logFile = sys.argv[4]

# Runs the thread with the timer
timer_runs = threading.Event()
timer_runs.set()
t = threading.Thread(target=timer, args=(timer_runs, intervalDuration))
t.start()
