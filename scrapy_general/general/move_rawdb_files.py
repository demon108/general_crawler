import os
import shutil
from config import DBFILE_MOVE_TARGET,DBFILE_MAKING_DIR

def move_db_files():
    if len(os.listdir(DBFILE_MAKING_DIR))!=0: 
        for db_file in os.listdir(DBFILE_MAKING_DIR):
            cur_file = DBFILE_MAKING_DIR+db_file
            shutil.move(cur_file,DBFILE_MOVE_TARGET)