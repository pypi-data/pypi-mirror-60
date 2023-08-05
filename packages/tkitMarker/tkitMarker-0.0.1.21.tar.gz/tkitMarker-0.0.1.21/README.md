# Bert-BiLSTM-CRF-pytorch
使用谷歌预训练bert做字嵌入的BiLSTM-CRF序列标注模型

本模型使用谷歌预训练bert模型（https://github.com/google-research/bert）， 
同时使用pytorch-pretrained-BERT（https://github.com/huggingface/pytorch-pretrained-BERT）
项目加载bert模型并转化为pytorch参数，CRF代码参考了SLTK（https://github.com/liu-nlper/SLTK）

准备数据格式参见data

模型参数可以在config中进行设置

运行代码

python main.py train --use_cuda=False --batch_size=10 

预测
python main.py test  --load_path result/pytorch_model.bin

python main.py test  --load_path result/pytorch_model.bin --use_cuda=False 


python main.py test --load_path data/bert/run



albert 版本

 <!-- 大约6.5g内存 -->
 <!-- 使用base模型 -->
 <!-- 下载模型 https://www.kaggle.com/terrychanorg/pytorch-albert-zh -->
python al_main.py train --use_cuda=False --batch_size=50 --base_epoch=1


python al_main.py test  --load_path tkitfiles/v0.1/pytorch_model.bin --use_cuda=False  --load_model=Ture --rnn_layer=2 --dropout_ratio=0.2 --dropout1=0.2

预测
python al_main.py pre_one --text "柯基犬真是和牛逼" --load_path tkitfiles/v0.1/pytorch_model.bin --use_cuda=False  --load_model=Ture --rnn_layer=2 --dropout_ratio=0.2 --dropout1=0.2

pytorch.bin  百度网盘链接   链接:https://pan.baidu.com/s/160cvZXyR_qdAv801bDY2mQ 提取码:q67r 

作者也是新手，很希望看到的大家能够提意见，共同学习
