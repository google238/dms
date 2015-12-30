__author__ = 'michael'
__metaclass__ = type
import web
from model import *
from config.config_default import *


class dms_model(model):
    def __init__(self):
        super(dms_model, self).__init__('dms_resource')