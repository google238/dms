__author__ = 'michael'
__metaclass__ = type
import web
from model import *
from config.config_default import *


class data_model(model):
    def __init__(self,name=None):
        super(data_model, self).__init__(name)