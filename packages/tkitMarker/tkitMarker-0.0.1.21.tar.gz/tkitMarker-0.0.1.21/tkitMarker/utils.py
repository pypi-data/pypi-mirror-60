# coding=utf-8
import torch
import os
import datetime
import unicodedata
import json

from random import sample


class InputFeatures(object):
    def __init__(self, input_id, label_id, input_mask):
        self.input_id = input_id
        self.label_id = label_id
        self.input_mask = input_mask


def load_vocab(vocab_file):
    """Loads a vocabulary file into a dictionary."""
    vocab = {}
    index = 0
    with open(vocab_file, "r", encoding="utf-8") as reader:
        while True:
            token = reader.readline()
            if not token:
                break
            token = token.strip()
            vocab[token] = index
            index += 1
    return vocab


def read_corpus(path, max_length, label_dic, vocab):
    """
    :param path:数据文件路径
    :param max_length: 最大长度
    :param label_dic: 标签字典
    :return:
    """
    # file = open(path, encoding='utf-8')
    # content = file.readlines()
    # file.close()
    result = []
    # with open(path, 'r', encoding = 'utf-8') as f:

    tjson=Tjson(file_path=path)

    for line in tjson.load():
        # text, label = line.strip().split('|||')
        
        # tokens = text.split()
        # label = label.split()
        # print(line)
        tokens=line['text']
        label=line['label']

        if len(tokens) > max_length-2:
            tokens = tokens[0:(max_length-2)]
            label = label[0:(max_length-2)]

        #自动屏蔽百分之15的数据
        for num in sample(range(1,len(tokens)),int(0.15*len(tokens))):
            tokens[num] ="[MASK]"

        tokens_f =['[CLS]'] + tokens + ['[SEP]']
        label_f = ["<start>"] + label + ['<eos>']
        input_ids = [int(vocab[i]) if i in vocab else int(vocab['[UNK]']) for i in tokens_f]
        label_ids = [label_dic[i] for i in label_f]
        input_mask = [1] * len(input_ids)
        while len(input_ids) < max_length:
            input_ids.append(0)
            input_mask.append(0)
            label_ids.append(label_dic['<pad>'])
        assert len(input_ids) == max_length
        assert len(input_mask) == max_length
        assert len(label_ids) == max_length
        feature = InputFeatures(input_id=input_ids, input_mask=input_mask, label_id=label_ids)
        result.append(feature)
    return result

class InputPreFeatures(object):
    def __init__(self, input_id, input_mask):
        self.input_id = input_id
        # self.label_id = label_id
        self.input_mask = input_mask

def build_input(content, max_length, vocab):
    """
    :param content: 输入句子列表
    :param max_length: 最大长度
    :return:
    """
    # file = open(path, encoding='utf-8')
    # content = file.readlines()
    # file.close()
    result = []
    for line in content:
        # text, label = line.strip().split('|||')
        tokens = line.split()
        # label = label.split()
        if len(tokens) > max_length-2:
            tokens = tokens[0:(max_length-2)]
            # label = label[0:(max_length-2)]
        # print(tokens)
        tokens_f =['[CLS]'] + tokens + ['[SEP]']
        # print('tokens_f',tokens_f)
        # label_f = ["<start>"] + label + ['<eos>']
        input_ids = [int(vocab[i]) if i in vocab else int(vocab['[UNK]']) for i in tokens_f]
        # label_ids = [label_dic[i] for i in label_f]
        input_mask = [1] * len(input_ids)
        while len(input_ids) < max_length:
            input_ids.append(0)
            input_mask.append(0)
            # label_ids.append(label_dic['<pad>'])
        assert len(input_ids) == max_length
        assert len(input_mask) == max_length
        # assert len(label_ids) == max_length
        feature = InputPreFeatures(input_id=input_ids, input_mask=input_mask)
        result.append(feature)
    return result



def save_model(model, epoch, path='result', **kwargs):
    """
    默认保留所有模型
    :param model: 模型
    :param path: 保存路径
    :param loss: 校验损失
    :param last_loss: 最佳epoch损失
    :param kwargs: every_epoch or best_epoch
    :return:
    """
    if not os.path.exists(path):
        os.mkdir(path)
    if kwargs.get('name', None) is None:
        # cur_time = datetime.datetime.now().strftime('%Y-%m-%d#%H:%M:%S')
        # name = cur_time + '--epoch:{}'.format(epoch)
        name="pytorch_model.bin"
        full_name = os.path.join(path, name)
        torch.save(model.state_dict(), full_name)
        # print('Saved model at epoch {} successfully'.format(epoch))
        with open('{}/checkpoint'.format(path), 'w') as file:
            file.write(name)
            # print('Write to checkpoint')


def load_model(model, path='result', **kwargs):
    if kwargs.get('name', None) is None:
        with open('{}/checkpoint'.format(path)) as file:
            content = file.read().strip()
            name = os.path.join(path, content)
    else:
        name=kwargs['name']
        # name = os.path.join(path,name)
        name = os.path.join(name)
    # print('name',name)
    model.load_state_dict(torch.load(name, map_location=lambda storage, loc: storage))
    # print('load model {} successfully'.format(name))
    return model


def save_config(config):
    """
    保存参数
    """
    # config = Config()
    # print(config)
    data={}
    for key,value in config.__dict__.items():
        # print(key,value)
        data[key] = value

    file = open(data['checkpoint']+"/config.json",'w',encoding='utf-8')
    json.dump(data,file,ensure_ascii=False)
    file.close()
    # sc=Tjson(file_path=data['checkpoint']+"/config.json")
    # sc.save([data])
    # pass
def load_json(path):
    """
    加载json文件
    """
    file = open(path,'r',encoding='utf-8')
    s = json.load(file)
    return s
#     with open(self.file_path, 'r', encoding = 'utf-8') as f:
#         line = json.dumps(item, ensure_ascii=False) 

class Tjson:
  """
  处理json信息函数
  """
  def __init__(self,file_path="data.json"):
    self.file_path=file_path
  def save(self,data):
    """
    保存数据函数
    逐行写入
    >>> data=[{'a':'ess'}]
    """
    with open(self.file_path, 'a+', encoding='utf-8') as f:
      for item in data:
        line = json.dumps(item, ensure_ascii=False)
        f.write(line+'\n')


  def load(self):
    """
    加载数据

    """
    with open(self.file_path, 'r', encoding = 'utf-8') as f:
        for line in f:
            try:
                # print(line)
                data=json.loads(line[:-1])
                # print(data)
                yield data
            except:
                pass
"""
#使用
data=[{'a':'ess'}]
Json().save(data)
print(Json().load())


"""