# -*- coding: utf-8 -*-

from mdsshellcommand import ShellCommandRun
from mdslogger import formatExceptionInfo


class NonePowerStrip:
    """ dummy driver
    """
    def __init__(self, jobname, logger):
        """ settings
        """
        self.__jobname = jobname
        self.__log = logger

    def __del__(self):
        """ clean up
        """
        pass

    def getNumPwrOutlets(self):
        """ get number of available power outets
        """
        return 4
    
    def getStatePwrOutlet(self, outletnr):
        """ queries the state of the power outlet,
            'outletnr' - nr of power outlet [1,...] 0 = all (list),
            retuen: True if active, False if inactive, None if error
        """
        return [False]
  
    def switchPwrOutlet(self, outletnr, state):
        """ answer success
        """
        return True

# ende NonePowerStrip
