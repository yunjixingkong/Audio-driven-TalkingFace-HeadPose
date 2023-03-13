# -*- coding: utf-8 -*-  
import yaml

class Config(object):
    def __init__(self,filename):
        self.filename = filename
        self.config = self.load_config()

    def load_config(self):
        with open(self.filename,'r',encoding='utf-8') as f:
            config = yaml.load(f,Loader=yaml.FullLoader)
        return config

    def NSQ(self):
        return self.config.get('Nsq')

    def Templates(self):
        return self.config.get('Templates')
    
    def OSS(self):
        return self.config.get('OSS')
    
    def WebHook(self):
        return self.config.get('WebHookURL')

    def Cache(self):
        return self.config.get('Cache')