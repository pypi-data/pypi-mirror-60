import os
import argparse
import shutil
from .clean import cleanwork
from loguru import logger

TASK_TEMPLATE = template = r"""from_path,to_path,condition,command,iscrawl
path1,path2,.*\.pyc$,delete,1
path3,path4,.*\.(exe|msi)$,move,0"""


def main():
    logger.info("Program start")
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="tasks.csv")
    parser.add_argument("--init", default=None, action="store_true")
    args = parser.parse_args()
    configPath = args.config
    logger.debug(f"Parser args: {args}")
    if args.init:
        initTasks()
    elif configPath:
        try:
            with open(configPath, "r") as f:
                config = f.read()
        except IOError as e:
            logger.error(e)
            return False
        runTasks(config)
    logger.info("Program end")


def runTasks(config):
    tasks = [x.split(",") for x in config.split("\n")][1:]  # Get config
    logger.info("{n} tasks found".format(n=len(tasks)))
    for task in tasks:
        if len(task) == 5:
            fromPath, toPath, pattern, command, iscrawl = task
            cleanwork(fromPath, toPath, pattern, command, iscrawl)


def initTasks(targetPath=None):
    defaultTargetPath = "tasks.csv"
    _targetPath = targetPath if targetPath else defaultTargetPath
    if not os.path.exists(_targetPath):
        with open(_targetPath, "w") as f:
            f.write(TASK_TEMPLATE)
    else:
        logger.info(f"{_targetPath} is exists")
