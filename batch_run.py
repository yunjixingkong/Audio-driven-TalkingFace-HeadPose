import os
import time
import sys

video=sys.argv[1]
n=int(os.path.splitext(video)[0])
# n=int(sys.argv[1])

# n = 1 #person id
gpu = 0
audio = 'shengma'

start_time = time.time()  

## finetuning on a target person
cmd1='cd Data/; python extract_frame_alpha.py %s' % video
os.system(cmd1)
first=time.time() - start_time

cmd2='cd Deep3DFaceReconstruction/; CUDA_VISIBLE_DEVICES=%d python demo_19news.py ../Data/%d' % (gpu,n)
os.system(cmd2)
second=time.time() - first

cmd3='cd Audio/code; python train_19news_1.py %d %d' % (n,gpu)
os.system(cmd3)
third=time.time() - second

cmd4='cd render-to-video; python train_19news_1.py %d %d' % (n,gpu)
os.system(cmd4)
four=time.time() - third

## test
# cmd5='cd Audio/code; python test_personalized2.py %s %d %d' % (audio,n,gpu)
# os.system(cmd5)
five=time.time() - four
total=time.time()-start_time
print(f"first {first}, seond {second}, third {third}, four {four}, five {five}. total {total}")