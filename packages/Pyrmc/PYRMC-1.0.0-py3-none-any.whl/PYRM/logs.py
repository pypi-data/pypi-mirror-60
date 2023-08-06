import os
from datetime import datetime
import sys

class logger:
    def __init__(self, path="logs", mode="debug"):
        self.mode=mode
        try:
            self.currentLog=datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
            try:
                os.mkdir("logs")
            except:
                pass
            self.log=open(f"{path}/log {self.currentLog}.txt", "a")
            self.log.write("logs start\n")
            self.log.close
            
        except:
            pass

    def write(self, level=0, text=""):
        try:
            if self.mode=="debug":
                print(f"log: {level} |{datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}| {text}\n")
            level=str(level)
            self.log.write(f"{level} |{datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}| {text}\n")
            self.log.close
            return 0
        except:
            return Exception
    
