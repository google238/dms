__author__ = 'michael'
__metaclass__ = type
import web
from model import *
from config.config_default import *


class userfrom_model(model):
	def __init__(self):
		super(userfrom_model, self).__init__('userfrom')