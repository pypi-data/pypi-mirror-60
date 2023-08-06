# Description:Clean files

import os
import re
from loguru import logger
from . import models


def cleanwork(fromPath, toPath, pattern, command, iscrawl=False, iter_times=0):
    """
    File clean up

    Parameters
    ----------
    fromPath:string
        Source folder
    toPath:string
        Target folder
    pattern:string
        Regular expression partern for file match
    command:string
        delete, move or copy
    iscrawl:bool,default is False
        is crawl fodler if exists nesting folders

    Returns
    -------
    None
    """
    task_name = "Task {0} {2} to {1} ".format(fromPath, toPath, command)
    logger.info("Start {task}".format(task=task_name))
    try:
        filenameList = os.listdir(fromPath)
        nfiles = len(filenameList)
        if nfiles == 0:
            logger.info(f"{nfiles} files found in {fromPath}.")
    except Exception as e:
        logger.error("Open %s error." % fromPath)
        logger.error(e)
        return None
    for filename in filenameList:
        newPath = fromPath + "/" + filename
        # Handling recursive problems with folders
        if os.path.isdir(newPath) and bool(int(iscrawl)) and iter_times < 10:
            iter_times += 1
            logger.info(newPath, iter_times)
            cleanwork(newPath, toPath, pattern, command, iscrawl, iter_times)
        elif re.match(pattern, filename, flags=re.IGNORECASE):
            Worker = models.selectWorker(command)
            worker = Worker(newPath, toPath, pattern)
            worker.work()
            logger.info("{task} done".format(task=task_name))
    # logger.info('{task} end'.format(task=task_name))
