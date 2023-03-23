n=3012
echo ${n}

rm -rf Audio/results/atcnet_pose0_con3/${n}
rm -rf Audio/model/atcnet_pose0_con3/${n}
rm -rf Audio/sample/atcnet_pose0_con3/${n}
rm -rf Audio/results/chosenbg/*

rm -rf Data/${n}

rm -rf Deep3DFaceReconstruction/output/coeff/19_news/${n}
rm -rf Deep3DFaceReconstruction/output/render/19_news/${n}

rm -rf render-to-video/arcface/iden_feat/19_news/${n}
rm -rf render-to-video/checkpoints/memory_seq_p2p/${n}
rm -rf render-to-video/datasets/list/testA/${n}_bmold_win3.txt
rm -rf render-to-video/datasets/list/testB/${n}_bmold_win3.txt
rm -rf render-to-video/datasets/list/trainA/${n}_bmold_win3.txt
rm -rf render-to-video/datasets/list/trainB/${n}_bmold_win3.txt
rm -rf render-to-video/results/memory_seq_p2p/${n}
