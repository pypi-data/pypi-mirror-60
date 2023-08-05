# coding=utf-8
import torch
from .utils import Tjson,load_json
class Config(object):
    def __init__(self):
        self.label_file = './data/tag.txt'
        self.train_file = './data/train.json'
        self.dev_file = './data/dev.json'
        self.test_file = './data/test.txt'
        self.conf = 'tdata/albert_tiny/config.json'
        # self.vocab = './data/bert/vocab.txt'
        self.vocab = './data/albert/vocab.txt'
        self.max_length = 50
        # device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        if torch.cuda.is_available():
            self.use_cuda = True
        else:
            self.use_cuda = False
              
        self.gpu = 0
        self.batch_size = 10
        self.bert_path = './data/bert'
        self.albert_path = './data/albert'
        self.rnn_hidden = 500
        self.bert_embedding = 768
        self.albert_embedding= 768
        self.dropout1 = 0.2
        self.dropout_ratio = 0.2
        self.rnn_layer = 2
        self.lr = 0.0001
        self.lr_decay = 0.00001
        self.weight_decay = 0.00005
        self.checkpoint = 'result/'
        self.optim = 'Adam'
        self.load_model = False
        self.load_path = None
        self.base_epoch = 10
    def load_config(self):
        try:
            conf=  load_json(self.conf)
            self.update_json(conf)
        except:
            pass

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    def update_json(self, args):
        """
        修改json版本数据
        """
        for k, v in args.items():
            setattr(self, k, v)
    def __str__(self):

        return '\n'.join(['%s:%s' % item for item in self.__dict__.items()])


if __name__ == '__main__':

    con = Config()
    con.update(gpu=8)
    print(con.gpu)
    print(con)
