import os, sys
import glob
import numpy as np
import pdb
from PIL import Image
import cv2
import threading
import timeit

import shutil

def merge_with_bigbg(audiobasen,n, output_path=None, proportion=None):
	start_time = timeit.default_timer()  # 设置计时器 
	start=0;ganepoch=60;audioepoch=99
	seamlessclone = 1
	person = str(n)
	print(f"merge_with_bigbg with proportion {proportion}")
	if os.path.exists(os.path.join('../audio/',audiobasen+'.wav')):
		in_file = os.path.join('../audio/',audiobasen+'.wav')
	elif os.path.exists(os.path.join('../audio/',audiobasen+'.mp3')):
		in_file = os.path.join('../audio/',audiobasen+'.mp3')
	else:
		print('audio file not exists, please put in %s'%os.path.join(os.getcwd(),'../audio'))
		return
	
	audio_exp_name = 'atcnet_pose0_con3/'+person
	audiomodel=os.path.join(audio_exp_name,audiobasen+'_%d'%audioepoch)
	sample_dir = os.path.join('../results/',audiomodel)
	ganmodel='memory_seq_p2p/%s'%person;
	post='_full9'
	seq='rseq_'+person+'_'+audiobasen+post
	if audioepoch == 49:
		seq='rseq_'+person+'_'+audiobasen+'_%d%s'%(audioepoch,post)

	coeff_dir = os.path.join(sample_dir,'reassign')

	sample_dir2 = '../../render-to-video/results/%s/test_%d/images%s/'%(ganmodel,ganepoch,seq)
	os.system('cp '+sample_dir2+'/R_'+person+'_reassign2-00002_blend2_fake.png '+sample_dir2+'/R_'+person+'_reassign2-00000_blend2_fake.png')
	os.system('cp '+sample_dir2+'/R_'+person+'_reassign2-00002_blend2_fake.png '+sample_dir2+'/R_'+person+'_reassign2-00001_blend2_fake.png')

	video_name = os.path.join(sample_dir,'%s_%swav_results%s.mp4'%(person,audiobasen,post))
	# command = 'ffmpeg -loglevel panic -framerate 25  -i ' + sample_dir2 +  '/R_' + person + '_reassign2-%05d_blend2_fake.png -c:v libx264 -y -vf format=yuv420p ' + video_name
	# os.system(command)
	# command = 'ffmpeg -loglevel panic -i ' + video_name + ' -i ' + in_file + ' -vcodec copy  -acodec copy -y  ' + video_name.replace('.mp4','.mov')
	# os.system(command)
	# os.remove(video_name)
	
	if not os.path.exists(os.path.join('../../Data',str(n),'transbig.npy')):
		cmd = 'cd ../../Deep3DFaceReconstruction/; python demo_preprocess.py %d %d' % (n,n+1)
		os.system(cmd)
	
	transdata = np.load(os.path.join('../../Data',str(n),'transbig.npy'))
	w2 = transdata[0]
	h2 = transdata[1]
	t0 = transdata[2]
	t1 = transdata[3]

	coeffs = glob.glob(coeff_dir+'/*.npy')
	transbigbgdir = os.path.join(sample_dir,'trans_bigbg')
	if not os.path.exists(transbigbgdir):
		os.mkdir(transbigbgdir)

	transbigbgdir_list=glob.glob(os.path.join(transbigbgdir, "*.png"))
	orig_list=glob.glob(os.path.join("../../Data/" + person,"*.png"))
	close_img="../../Data/" + person+"/frame32.png"
	print(f"transbigbgdir: {transbigbgdir}, close: {close_img}")
	begin = 0

	orig_len=len(orig_list)

	# 使用切片功能把大列表分成多个小列表   
	p_count=20
	b_size=len(coeffs)//p_count
	sub_coeffs = [coeffs[i:i+b_size] for i in range(0, len(coeffs), b_size)]   
	
	def merge(start, coeffs):
		# f = FaceLandmark()
		# orig_pos=0
		# blink=start+random.randint(1,5)*25 # 按照25fps，每秒15-20次眨眼
		for i in range(len(coeffs)):
			pos=start+i
			data = np.load(coeff_dir+'/%05d.npy'%pos)
			assigni = data[-1]
			if seamlessclone == 0:
				# direct paste
				img = Image.open('../../Data/'+person+'/frame%d.png'%assigni)
				img1 = Image.open(sample_dir2+'/R_'+person+'_reassign2-%05d_blend2_fake.png'%pos)
				img1 = img1.resize((w2,h2),resample = Image.LANCZOS)
				img.paste(img1,(t0,t1,t0+img1.size[0],t1+img1.size[1]))
				img.save(os.path.join(transbigbgdir,'%05d.png'%pos))
			else:
				# seamless clone
				png_path='../../Data/'+person+'/frame%d.png'%assigni
				# print(png_path)
				img = cv2.imread(png_path, cv2.IMREAD_UNCHANGED)
				img1 = cv2.imread(sample_dir2+'/R_'+person+'_reassign2-%05d_blend2_fake.png'%pos)
				img1 = cv2.resize(img1,(w2,h2),interpolation=cv2.INTER_LANCZOS4)

				# Convert the image to RGBA
				# img1 = cv2.cvtColor(img1, cv2.COLOR_RGB2RGBA)
				# Load the mask numpy array
				# mask_np = np.load('../../Data/'+person+'/frame%d.npy'%assigni)

    
				# 默认整张脸
				# mask = np.ones(img1.shape,img1.dtype) * 255
				# center = (t0+int(img1.shape[0]/2),t1+int(img1.shape[1]/2))

				# 嘴部矩形融合
				# mask1,center1, nose1=f.get_mask_center(img,15)
				# mask, center,nose = f.get_mask_center(img1, 5)
				# mask=mask.astype(np.uint8)
				# center = (t0+center[0],t1+center[1])
   
				# 半张脸融合
				# mask = np.ones(img1.shape,img1.dtype) * 255
				# mask[0:int(h2/2),:,0:3] = 0
				# center = (t0+int(img1.shape[0]/2),t1+int(img1.shape[1]-h2/4))
        
				# 2/5张脸融合
				# mask = np.ones(img1.shape,img1.dtype) * 255
				# mask[0:int(h2/5*3),:,0:3] = 0
				# center = (t0+int(img1.shape[0]/2),t1+int(img1.shape[1]-h2/5))

				# 45/100张脸融合
				s=proportion
				if s is None:
					s=0.35
				mask = np.ones(img1.shape,img1.dtype) * 255
				mask[0:int(h2*(1-s)),:,0:3] = 0
				center = (t0+int(img1.shape[0]/2),t1+int(img1.shape[1]-h2*(s/2)))

				# 鼻子以下融合
				# mask = np.ones(img1.shape,img1.dtype) * 255
				# mask[0:int(nose[1]),:,0:3] = 0
				# pad_x, pad_y = int(t0+nose[0]-nose1[0]), int(t1+nose[1]-nose1[1])
				# center = (t0+int(img1.shape[0]/2), t1+int((img1.shape[1]-nose[1])/2+nose[1])-pad_y)
				# center = (t0+int(img1.shape[0]/2), t1+int((img1.shape[1]-h2/5)))

				# 检查图像是否具有alpha通道
				has_alpha = img.shape[2] == 4
				if has_alpha:
					# 从源图像中提取alpha通道
					src_alpha = img[:,:,3]
					# 从源图像中删除alpha通道
					img = img[:,:,0:3]


				output = cv2.seamlessClone(img1,img,mask,center,cv2.NORMAL_CLONE)
    
				if has_alpha:
					# 将输出图像分离为其颜色通道
					b, g, r = cv2.split(output)
					a = np.load('../../Data/'+person+'/frame%d.npy'%assigni)
					a = 255-a
					# a = src_alpha
					output = cv2.merge((b, g, r, a))

				# data_tmp=np.load(png_path.replace(".png", ".npy"), allow_pickle=True).item()
				# if data_tmp["close"]:
				# 	output = swap_orgin_data_with_landmark(output, img,f.get_landmark(output), data_tmp["landmarks"],'eye')
    
				# data_tmp=np.load(png_path.replace(".png", ".npy"), allow_pickle=True).item()
				# if data_tmp["close"] == True:
				# 	img_orig = cv2.imread(png_path)
				# 	output = swap_orgin_data_with_landmark(output, img_orig,f.get_landmark(output), data_tmp["landmarks"],'eye', True)
				
				# 逐帧拷贝眼部区域
				# orig_pos = pos%orig_len
				# data_tmp=np.load(orig_list[orig_pos].replace(".png", ".npy"), allow_pickle=True).item()
				# img_orig = cv2.imread(orig_list[orig_pos])
				# output = swap_orgin_data_with_landmark(output, img_orig,f.get_landmark(output), data_tmp["landmarks"],'eye', data_tmp["close"])
    
    	
				# if pos==blink:
				# 	orig_pos = pos%orig_len
				# 	# img_orig = cv2.imread(orig_list[orig_pos])
				# 	img_orig = cv2.imread(orig_list[32])
				# 	output = swap_orgin_data_with_landmark(output, img_orig,f.get_landmark(output), f.get_landmark(img_orig),'eye')
				# 	blink=pos+random.randint(4,10)*25
				cv2.imwrite(os.path.join(transbigbgdir,'%05d.png'%pos),output)

	threads = []
	for i in range(len(sub_coeffs)):
		t = threading.Thread(target=merge, args=(i*b_size,sub_coeffs[i]))
		threads.append(t)
		t.start()
	for t in threads:
		t.join()

	transbigbgdir = os.path.join(sample_dir,'trans_bigbg')
	video_name = os.path.join(sample_dir,'%s_%swav_results_transbigbg.mp4'%(person,audiobasen))
	# command = 'ffmpeg -loglevel panic -framerate 25  -i ' + transbigbgdir +  '/%05d.png -c:v libx264 -y -vf format=yuv420p ' + video_name
	# os.system(command)
	# command = 'ffmpeg -loglevel panic -i ' + video_name + ' -i ' + in_file + ' -vcodec copy  -acodec copy -y  ' + video_name.replace('.mp4','.mov')
	# os.system(command)
 
	# 兼容macos的quickplayer播放：ffmpeg -r 25 -i ../results/atcnet_pose0_con3/20/shengma_s_99/trans_bigbg/%05d.png -i ../audio/shengma_s.wav -c:v prores_ks -profile:v 5  -bits_per_mb 8000 -pix_fmt yuva422p10le output.mov
	# command = 'ffmpeg -framerate 25 -i ' + transbigbgdir +  '/%05d.png -i '+ in_file + ' -c:v prores_ks -profile:v 5  -bits_per_mb 8000 -pix_fmt yuva422p10le -y ' + video_name.replace('.mp4','.mov')
	# ffmpeg -r 25 -i ../results/atcnet_pose0_con3/20/shengma_s_99/trans_bigbg/%05d.png -i ../audio/shengma_s.wav -vcodec png -acodec aac -y output_video.mov
	# command = 'ffmpeg -framerate 25 -i ' + transbigbgdir +  '/%05d.png -i '+ in_file + ' -vcodec png -acodec aac -y ' + video_name.replace('.mp4','.mov')
	# print(command)
	# os.system(command)

	# command = 'ffmpeg -thread_queue_size 4096 -framerate 25 -i ' + transbigbgdir + '/%05d.png -i '+ in_file + ' -c:v libvpx-vp9 -threads 16 -pix_fmt yuva420p -metadata:s:v:0 alpha_mode="1" -b:v 2M -b:a 16K -y ' + video_name.replace('.mp4','.webm')
	command = 'ffmpeg -thread_queue_size 4096 -framerate 25 -i ' + transbigbgdir + '/%05d.png -i '+ in_file + ' -c:v libvpx -pix_fmt yuva420p -cpu-used 8 -auto-alt-ref 0 -metadata:s:v:0 alpha_mode="1" -b:v 2M -b:a 16K -y ' + video_name.replace('.mp4','.webm')
	print(command)
	os.system(command)

	if output_path != None:
		shutil.move(video_name.replace('.mp4','.webm'), output_path)
	shutil.rmtree(sample_dir2)
	elapsed = timeit.default_timer() - start_time  # 计算函数执行时长 
	print(f"merge_with_bigbg elapsed {elapsed}")
	print('saved to', video_name.replace('.mp4','.webm'))

audiobasen=sys.argv[1]
n = int(sys.argv[2])

if __name__ == "__main__":
	merge_with_bigbg(audiobasen,n)
