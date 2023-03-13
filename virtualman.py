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

TEXT           = "Text"
ORIGINAL_VOICE = "OriginalVoice"
MODULATE_VOICE = "ModulateVoice"

parser = argparse.ArgumentParser()
parser.add_argument('--config', type=str, default='conf/default.yaml', help='config file')

audio_cache="/tmp/videocache"

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
    inputSsml = task_dict.get("InputSsml")
    timbreKey = task_dict.get("TimbreKey")
    videoFormat = task_dict.get("VideoFormat")
    driverType = task_dict.get("DriverType")
    inputAudioUrl = task_dict.get("InputAudioUrl")
    videoStorageS3Url = task_dict.get("VideoStorageS3Url")
    subtitleStorageS3Url = task_dict.get("SubtitleStorageS3Url")
    speed = task_dict.get("Speed")
    
    audio = ""
    if driverType != TEXT:
        audio = download_wget(inputAudioUrl, "./Audio/audio") 
    
    if driverType == TEXT:
        audio=os.path.join("./Audio/audio", f"{taskId}.wav")
        _TTSModel.infer(timbreKey, inputSsml, output=audio) 
    
    inputAudioUrl=unquote(inputAudioUrl) 
    videoStorageS3Url=unquote(videoStorageS3Url) 
    subtitleStorageS3Url=unquote(subtitleStorageS3Url)
    inputSsml=unquote(inputSsml)
    video=os.path.join(audio_cache, f"{taskId}.mp4")
    command=f"cd ./Audio/code; python prod.py {os.path.basename(audio)[:-4]} {virtualmanKey} 0 {video}"
    print(command)
    os.system(command)
    upload_with_put(local_file=video, url=videoStorageS3Url)

    complet_req["Progress"]=100
    complet_req["Status"]="SUCCESS"
    complet_req["MediaUrl"] = videoStorageS3Url
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
    r = nsq.Reader(message_handler=nsq_handler,lookupd_http_addresses=nsqcfg.get("Hosts"), topic='virtualman_video_task_create', channel='pyworker', lookupd_poll_interval=15)
    nsq.run() #tornado.ioloop.IOLoop.instance().start()
