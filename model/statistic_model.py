__author__ = 'michael'
__metaclass__ = type
import web
from modelstatistic import *
from config.config_default import *


class statistic_model(modelstatistic):
    def __init__(self,name=None):
        super(statistic_model, self).__init__(name)