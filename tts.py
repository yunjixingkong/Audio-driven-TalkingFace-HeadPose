#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :    worker.py
@Time    :    2022/12/07 12:06:44
@Author  :    baronzhang
@Version :    1.0
@Contact :    
@Desc    :    
'''
import os
import nsq
import argparse
import json
import threading
import requests
import time
import wget

from urllib.parse import quote, unquote, urlencode

from helper.config import Config
from helper.log import logger
from helper.upload import upload_with_put
from helper.tts_modelscope import ModelScopeTTS
from helper.file_uploader import MinioClient

parser = argparse.ArgumentParser()
parser.add_argument('--config', type=str, default='conf/default.yaml', help='config file')

audio_cache="/tmp/ttscache"

def download_oss(url, cache_path):
    file_name = os.path.basename(url)
    cache_file= os.path.join(cache_path,file_name)
    if os.path.exists(cache_file) == False: 
         _OSSClient.download(bucket_name="static", object_name=file_name, file_path=cache_file)
    return cache_file

def download_wget(url, cache_path):
    logger.info("download url {} to {}".format(url, cache_path))
    file_name = wget.filename_from_url(url)
    cache_file= os.path.join(cache_path,file_name)
    if os.path.exists(cache_file) == False: 
        file_name = wget.download(url, out=cache_file)
    return cache_file

# http post请求
def http_report(url:str, data):
    headers = {'Content-Type': 'application/json'}
    datas = json.dumps(data)
    r = requests.post(url=url, data=datas, headers=headers)
    logger.info("new task report rsp: {}".format(r.text))


def process_all(message):
    task_dict=json.loads(str(message.body, encoding='utf-8'))
    logger.info("new task info: {}".format(task_dict))
    url=_Config.WebHook()
    cache = _Config.Cache()
    complet_req={
        "TaskId": task_dict.get("TaskId"),
        "Status": "MAKING",
    }
    # 上报开始制作
    http_report(url=url, data=complet_req) 
    logger.info("new task report start: {}".format(complet_req))
    taskId = task_dict.get("TaskId")
    virtualmanKey = task_dict.get("VirtualmanKey")
    timbreKey = task_dict.get("TimbreKey")
    inputSsml = task_dict.get("InputSsml")
    speed = task_dict.get("Speed")
    audioStorageS3Url = task_dict.get("AudioStorageS3Url")

    if len(timbreKey) == 0:
        timbreKey="zhiyan"

    audioStorageS3Url=unquote(audioStorageS3Url) 
    inputSsml=unquote(inputSsml)

    audio=os.path.join(audio_cache, f"{taskId}.wav")
    _TTSModel.infer(timbreKey, inputSsml, output=audio) 
    
    remote_url=""
    if len(audioStorageS3Url)> 0:
        upload_with_put(local_file=audio, url=audioStorageS3Url)
        remote_url=audioStorageS3Url
    else:
        try:
            remote_url=_OSSClient.upload(bucket_name=oss.get("Bucket"), object_name=f"{taskId}.wav", file_path=audio)
            if oss.get("Secure"):
                remote_url = "https://%s/%s/%s" % (oss.get("Host"), oss.get("Bucket"), f"{taskId}.wav")
            else:
                remote_url = "http://%s/%s/%s" % (oss.get("Host"), oss.get("Bucket"), f"{taskId}.wav")
                
        except Exception as result:
            logger.exception("gan exception {}".format(result))
            http_report(url=url, data=complet_req) 
            return None
    
    complet_req["Progress"]=100
    complet_req["Status"]="SUCCESS"
    complet_req["MediaUrl"] = remote_url
    http_report(url=url, data=complet_req) 
    os.remove(audio)

def nsq_handler(message):
    # 异步起动多个线程处理
    thread_one = threading.Thread(target=process_all, args=(message,))
    
    thread_one.start()
    while thread_one.is_alive() == True:
        time.sleep(1)
        message.touch() # 告知NSQD您需要更多时间来处理消息
    
    return True

if __name__ == '__main__':
    args = parser.parse_args()
    _Config = Config(args.config)
    t = time.time()
    oss=_Config.OSS()
    _OSSClient = MinioClient(endpoint=oss.get("Host"), access_key=oss.get("AccessKeyID"), secret_key=oss.get("SecretKey"), secure=oss.get("Secure"))

    os.makedirs(audio_cache, exist_ok=True)
    _TTSModel = ModelScopeTTS()

    nsqcfg=_Config.NSQ()
    r = nsq.Reader(message_handler=nsq_handler,lookupd_http_addresses=nsqcfg.get("Hosts"), topic='virtualman_tts_task_create', channel='pyworker', lookupd_poll_interval=15)
    nsq.run() #tornado.ioloop.IOLoop.instance().start()
