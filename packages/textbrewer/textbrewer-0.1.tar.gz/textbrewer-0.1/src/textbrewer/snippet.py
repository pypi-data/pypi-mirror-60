from textbrewer import GeneralDistiller
from textbrewer import TrainingConfig, DistillationConfig

# We omit the initialization of models, optimizer, and dataloader. 
teacher_model : torch.nn.Module = ...
student_model : torch.nn.Module = ...
dataloader : torch.utils.data.DataLoader = ...
optimizer : torch.optim.Optimizer = ...
scheduler : torch.optim.lr_scheduler = ...

def simple_adaptor(batch, model_outputs):
    # We assume that the first element of model_outputs 
    # is the logits before softmax
    return {'logits': model_outputs[0]}  

train_config = TrainingConfig()
distill_config = DistillationConfig()
distiller = GeneralDistiller(
    train_config=train_config, distill_config = distill_config,
    model_T = teacher_model, model_S = student_model, 
    adaptor_T = simple_adaptor, adaptor_S = simple_adaptor)

distiller.train(optimizer, scheduler, 
    dataloader, num_epochs, callback=None)



def predict(model, eval_dataset, step, args): 
  raise NotImplementedError
# 填充多余的参数
my_callback = partial(predict, eval_dataset=my_eval_dataset, args=args) 
train_config = TrainingConfig()

'''
class MyModel():
	def forward(self,input_ids, attention_mask, labels, ...):
		...
		return logits, sequence_output, total_loss

logits : Tensor of shape(batch_size, num_classes)
sequence_output : List of tensors of (batch_size, length, hidden_dim)
total_loss : scalar tensor

模型的输入为:
input_ids      = batch[0] : input_ids of shape (batch_size, length)
attention_mask = batch[1] : attention_mask of shape (batch_size, length)
labels         = batch[2] : labels (batch_size, num_classes)
...
'''
def SimpleAdaptor(batch, model_outputs):
  return {'logits': (model_outputs[0],),
          'hidden': model.outputs[1],
          'inputs_mask': batch[1]}  


# 自定义的预测与评估函数
def predict(model, eval_dataset, step, args): 
  '''
  eval_dataset: 验证集
  args: 评估中需要的其他参数
  '''
  raise NotImplementedError

 # 填充多余的参数
my_callback = partial(predict, eval_dataset=my_eval_dataset, args=args) 
distillator.train(..., callback = my_callback)



class MyModel(nn.Module)):
	def forward(self,input_ids, attention_mask, labels, ...):
		...
		return logits, sequence_output, total_loss

# tuple形式
dataset = TensorDataset(all_input_ids, all_attention_mask, all_labels)

# dict 形式
class DictDataset(Dataset):
    def __init__(self, all_input_ids, all_attention_mask, all_labels):
        assert len(all_input_ids)==len(all_attention_mask)==len(all_labels)
        self.all_input_ids = all_input_ids
        self.all_attention_mask = all_attention_mask
        self.all_labels = all_labels

    def __getitem__(self, index):
        return {'input_ids': self.all_input_ids[index],
                'attention_mask': self.all_attention_mask[index],
                'labels': self.all_labels[index]}
    
    def __len__(self):
        return self.all_input_ids.size(0)
dataset = DictDataset(all_input_ids, all_attention_mask, all_labels)

dataloader = Dataloader(dataset, batch_size = batch_size, drop_last=True)



 {"temperature": 8,
  "temperature_scheduler": 'none'
  "hard_label_weight": 0,
  "hard_label_weight_scheduler": 'none',
  "kd_loss_type": "ce",
  "kd_loss_weight": 1,
  "kd_loss_weight_scheduler": 'none',
  "probability_shift": False,
  "intermediate_matches": [
  {'layer_T':0, 'layer_S':0, 'feature':'hidden', 
   'loss': 'hidden_mse', 'weight' : 1,'proj':['linear',312,768]},
  {'layer_T':3, 'layer_S':1, 'feature':'hidden', 
  'loss': 'hidden_mse',  'weight' : 1,'proj':['linear',312,768]},
  {'layer_T':6, 'layer_S':2, 'feature':'hidden',  
  'loss': 'hidden_mse',  'weight' : 1,'proj':['linear',312,768]},
  {'layer_T':9, 'layer_S':3, 'feature':'hidden',  
  'loss': 'hidden_mse',  'weight' : 1,'proj':['linear',312,768]},
  {'layer_T':12, 'layer_S':4, 'feature':'hidden',  
  'loss': 'hidden_mse',  'weight' : 1,'proj':['linear',312,768]},
  {'layer_T':[0,0], 'layer_S':[0,0], 'feature':'hidden', 
   'loss': 'nst', 'weight': 1}
  {'layer_T':[3,3], 'layer_S':[1,1], 'feature':'hidden', 
   'loss': 'nst', 'weight': 1}
  {'layer_T':[6,6], 'layer_S':[2,2], 'feature':'hidden', 
   'loss': 'nst', 'weight': 1}
  {'layer_T':[9,9], 'layer_S':[3,3], 'feature':'hidden', 
   'loss': 'nst', 'weight': 1}
  {'layer_T':[12,12],'layer_S':[4,4], 'feature':'hidden',
   'loss': 'nst', 'weight': 1}]}