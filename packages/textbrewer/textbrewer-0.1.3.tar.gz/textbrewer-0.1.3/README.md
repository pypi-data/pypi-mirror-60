# Distillation Toolkit

**Distillation Toolkit** 是一个基于PyTorch的、提供快速实现**NLP中的知识蒸馏**的工具包。

**知识蒸馏**以较低的性能损失压缩神经网络模型的大小，提升模型的推理速度，减少内存占用。

**Distillation Toolkit** 包含了：

* 常用蒸馏方法（BasicDistillation、MultiTeacherDistillation、MultiTaskDistillation）
* 预定义损失函数(soft-label crossentropy, attention match, hidden states match, gram matrices match, ... ) 
* 训练循环

用户只需提供模型本身（已训练好的**教师**模型, 未训练的**学生**模型）、训练数据与必要的实验配置， 即可通过蒸馏压缩模型。

# 内容导引

[Features](#features)

[Requirements](#requirements)

[Workflow](#workflow)

[Quickstart](#quickstart)

## Features

* 方便灵活：适用于多种模型结构（主要面向**Transfomer**结构）
* 扩展性强：有众多可调参数，支持增加自定义蒸馏损失
* 非侵入式：无需对教师与学生模型本身结构进行修改
* 支持典型的NLP任务：文本分类、阅读理解、序列标注……

## Requirements

* Python >= 3.6
* PyTorch >= 1.1.0
* TensorboardX or Tensorboard

## Workflow

![](distillation_workflow.png)

* **Stage 1**: 训练教师模型
* **Stage 2**: 蒸馏教师模型，得到学生模型

用户应先实现 **stage 1** ，得到训练好的教师模型；**Distillation Toolkit** 负责 **Stage 2**的蒸馏工作。

完整的workflow的例子可参见 XXX.py (#TODO)

## Quickstart

```python
from distilltool import DistillConfig, TrainingConfig, Distillation

'''
构造并初始化教师模型model_T, 学生模型model_S, 
优化器 optimizer 和数据集 dataloader
'''

# 训练配置
train_config = TrainingConfig(...)
#蒸馏配置
distill_config = DistillationConfig(...)
#构造蒸馏器
distillator = Distillation(train_config = train_config,
                           distill_config = distill_config,
                           model_T = model_T, model_S = model_S,
                           adaptor_T = adaptor_T, adaptor_S = adaptor_S)
#蒸馏
with distillator:
  distillator.train(optimizer=optimizer, scheduler=scheduler,
                    dataloader=dataloader, num_train_epochs=num_train_epochs,
                    callback=your_callback, **args)
```

## 基本概念

### 变量与规范 

* **Model_T** : torch.nn.Module的实例。教师模型，一般来说参数量等于大于学生模型。

* **Model_S**：torch.nn.Module的实例。学生模型，蒸馏的目标模型，相对教师模型速度更快、体积更小。

* **optimizer**：torch.optim.Optimizer的实例。

* **scheduler**：torch.optim.lr_scheduler下的类的实例，提供单独的学习率调整策略。

* **dataloader** : 迭代器，用于获取 batch，一般用torch.utils.data.Dataloader构造。batch的类型可以是tuple或dict:

  ```python
  for batch in dataloader:
    # do with batch
    #...
    # 前向计算
  ```

  **注意：** 训练循环中会判断batch是否是dict。如果是dict，那么以model(\*\*batch, \*\*args) 的形式调用model，否则以 model(\*batch, \*\*args)的形式调用model。所以当batch不是dict时，**注意batch中每个元素的顺序和model接受的参数的顺序相一致**。args则用于传递额外的参数。

* **callback** : 回调函数。在每个checkpoint，保存模型后会调用callback，并传入参数 model=model_S, step=global_step。可用作在每个checkpoint评测模型效果。**如果在callback中评测模型，别忘了调用 model.eval()**。callback的签名为：

* ```python
  callback(model: torch.nn.Module, step: int) -> Any
  ```

* **adaptor_T** 和 **adaptor_S** : 将模型的输入和输出转换为指定的格式，以便蒸馏时计算损失。在每个训练步，batch和模型的输出model_outputs会作为参数传递给adaptor，adaptor负责重新组织这些数据，返回一个dict（以下分别称作**results_T和results_S**)：

  ```python
    adatpor(batch: Union[Dict,Tuple], model_outputs: Tuple) -> Dict
  ```

  dict的key和value为：

  * '**logits**' : List[torch.tensor] or torch.tensor : 类型为list of tensor 或 tuple of tensor 或 tensor ，表示需要计算蒸馏损失的logits，通常为模型最后softmax之前的输出。列表中每一个tensor形状为 (batch_size, num_labels) 或 (batch_size, length, num_labels)
  
  * '**logits_mask**' : List[torch.tensor] or torch.tensor:  0/1矩阵，对logits的某些位置做mask，类型为list of tensor 或 tuple of tensor 或 tensor。如果不想对logits某些位置计算损失，用mask遮掩掉。列表中每一个tensor的形状为 (batch_size, length)
  
    **注意**: 
  
    	1. logits_mask 仅对形状为 (batch_size, length, num_labels) 的 logits 有效，用于在length维度做mask
  
   	2. logits 和 logits_mask 要么同为 list/tuple of tensor, 要么都是tensor。
  
  * ’**losses**' : List[torch.tensor] : 如果模型中已经计算了一些损失并想利用这些损失训练，例如对ground-truth的交叉熵，可放在这里。训练时 'losses'下的所有损失将求和并乘以**hard_label_weight**,和蒸馏的损失加在一起做backward。列表中每一个tensor应为scalar，即shape为[]
  
  * '**attention**': List[torch.tensor] :attention矩阵的列表，用于计算中间层特征匹配。每个tensor的形状为 (batch_size, num_heads, length, length) 或 (batch_size, length, length) ，取决于应用于attention的损失的选取。各种损失函数详见**损失函数** (TODO)
  
* '**hidden**': List[torch.tensor] :hidden_states的列表，用于计算中间层特征匹配。每个tensor的形状为(batch_size, length,hidden_dim)
  
  * '**inputs_mask**' : torch.tensor : 0/1矩阵，对'attention'和“hidden'中张量做mask。形状为 (batch_size, length)
  
  这些key**都是可选**的：
  
  * 如果没有inputs_mask或logits_mask，则视为不做masking，或者说相应的mask全为1
  * 如果不做相应特征的中间层特征匹配，可不提供'attention'或'hidden'
  * 如果不想利用有标签数据上的损失，或者hard_label_weight==0，可不提供'losses'
  * 如果不提供'logits'，会略去最后输出层的蒸馏损失的计算
  * 当然也不能什么都没有，那就不会进行任何训练。
  
  Adaptor的作用可见下方示意图。**一般情况下，除非做multi-stage的训练，'logits' 是必须要有的。**



![](trainingloop.png)



### 类

* **DistillConfig**：蒸馏相关的配置
* **TrainConfig**：训练相关的配置
* **BasicDistillation**：基础蒸馏类，提供最经典/简单的soft-label+hard-label蒸馏方式，**不支持中间层特征匹配**。可作为调试或测试使用。
* **BasicTraining**：用于单个模型的普通方式训练，而非蒸馏。**可用于单独训练教师模型**。
* **Distillation**：实现单模型蒸馏，支持各种蒸馏损失。**一般情况下推荐使用**。
* **MultiTeacherDistillation**: 多教师蒸馏。将多个（同任务）教师模型蒸馏到一个学生模型上。**不支持中间层特征匹配**。
* **MultiTaskDistillation**：多任务蒸馏。将多个（不同任务）单任务教师模型蒸馏到一个多任务学生模型上。**不支持中间层特征匹配**。



## Usage

* 第零步：准备工作：模型、数据、优化器，回调函数，适配器：

  ```python
  #初始化教师与学生模型 
  model_T = MyTeacherModel()
  model_S = MyStudentModel()
  
  #教师模型载入训练好的权重
  model_T.load_state_dict(...)   
  model_T.to(device)
  model_S.to(device)
  #支持 DataParallel并行
  #model_T = torch.nn.DataParallel(model_T)
  #model_S = torch.nn.DataParallel(model_S)
  
  #初始化训练数据集
  dataloader = DataLoader(my_dataset, ... ) 
  
  #初始化优化器与scheduler(如果有)。注意训练参数里只需要传入学生的参数。
  #比如初始化Adam
  optimizer = torch.optim.Adam(model_S.parameters(), lr=my_lr,...)
  scheduler = None # 可选：如果不使用学习率调整策略或学习率调整策略已被optimizer实现，可设为None
  
  #定义回调函数，可选。将在每个checkpoint后被调用。函数签名：
  #callback_fun(model: nn.Module, step: int) -> None
  #model和step分别是学生模型和当前训练步数
  #这里的例子为：callback用于在验证集上测试模型
  def predict(model, eval_dataset, step, args): # 自定义的预测与评估函数,
    '''
    eval_dataset: 验证数据集
    args: 评估中需要的其他参数
    '''
    raise NotImplementedError
   
  callback_fun = partial(predict, eval_dataset=my_eval_dataset, args=args) # 填充多余的参数
  
  #定义adaptor，使得模型的输出能被Distillation识别
  # adaptor(batch,model_outputs) -> Dict
  def my_adaptor_T(batch, model_outputs):
    raise NotImplementedError
   
  def my_adaptor_T(batch, model_outputs):
    raise NotImplementedError
  ```

  

* 第一步：import 相关的类：

  ```python
  from distilltool import DistillConfig, TrainingConfig, Distillation
  ```

* 第二步：初始化训练与蒸馏配置，创建蒸馏器：

  ```python
  train_config = TrainingConfig()
  distill_config = DistillationConfig()
  distillator = Distillation(
    train_config   = train_config,
    distill_config = distill_config,
    model_T = model_T, model_S = model_S,
    adaptor_T = my_adaptor_T,
    adaptor_S = my_adaptor_S)
  ```

* 第三步：训练。在每个checkpoint处，模型会自动存储，并且调用callback_fun

  ```python
  with distillator:
    distillator.train(optimizer, scheduler, dataloader, num_epochs, callback_fun)
  ```

  

  

## 类型与参数说明

### 训练与蒸馏配置

class **TrainingConfig** (**gradient_accumulation_steps** = 1, **ckpt_frequency** = 1, **ckpt_epoch_frequency**=1, **log_dir** = './logs', **output_dir** = './saved_models', **device** = 'cuda'):

* **gradient_accumulation_steps** (int) : 梯度累加以节约显存。每计算 *gradient_accumulation_steps* 个batch的梯度，调用一次optimizer.step()。大于1时用于在大batch_size情况下节约显存。
* **ckpt_frequency** (int) : 存储模型权重的频率。每训练一个epoch储存模型权重的次数
* **ckpt_epoch_frequency** (int)：每多少个epoch储存模型
  * **ckpt_frequency**=1, **ckpt_epoch_frequency**=1 : 每个epoch结束时存一次 （默认行为）
  * **ckpt_frequency**=2, **ckpt_epoch_frequency**=1 : 在每个epoch的一半和结束时，各存一次
  * **ckpt_frequency**=1, **ckpt_epoch_frequency**=2 : 每两个epoch结束时，存一次
  * **ckpt_frequency**=2, **ckpt_epoch_frequency**=2 : 每2个epoch，仅在第2个epoch的一半和结束时各存一次（一般不会这样设置）
* **log_dir** (str) : 存放tensorboard日志的位置
* **output_dir** (str) : 储存模型权重的位置
* **device** (str, torch.device) : 在CPU或GPU上训练

示例：

```python
#一般情况下，除了log_dir和output_dir自己设置，其他用默认值即可
train_config = TrainingConfig(log_dir=my_log_dir, output_dir=my_output_dir)
```

* (classmethod) **TrainingConfig.from_json_file**(json_file : str) :
  * 从json文件读取配置

* (classmethod) **TrainingConfig.from_dict**(dict_object : Dict) :
  * 从字典读取配置

class **DistillationConfig** (**temperature** = 4, **hard_label_weight** = 0, **kd_loss_weight**=1, **kd_loss_type** = 'ce', **intermediate_matches** = None):

* **temperature** (float) : 蒸馏的温度。计算kd_loss时教师和学生的logits将被除以temperature。

* **kd_loss_weight** (float): adaptor_S返回的字典results_S中的'logits'项上的知识蒸馏损失权重。

* **hard_label_weight** (float) : results_S中的'losses'项之和的权重。一般来说'losses'项是Groud-truth上的损失权重。若**hard_label_weight**>0，且在adaptor中提供了 'losses'，那么最终的total_loss将包含：
  
  ​		$$kd\_loss\_weight * kd\_loss + hard\_label\_weight * sum(losses)$$
  
* **kd_loss_type** (str) : 模型最后输出的logits上的蒸馏损失函数。有效取值见 **KD_LOSS_MAP**。常可用的有：
  
  * 'ce': 计算学生和教师的logits的交叉熵损失 。大多数情况下使用'ce'可获得较好的效果
  * 'mse':计算学生和教师的logits的mse损失 
  
* **intermediate_matches** (List[Dict]) : 可选，模型中间层匹配损失的配置，list的每一个元素为一个字典，表示一对匹配配置。字典的key如下：
  
  * 'layer_T' : layer_T (int) : 选取教师的第layer_T层
  
  * 'layer_S' : layer_S (int) : 选取学生的第layer_S层
  
    **注意**：**layer_T 和 layer_S选取的层数是adaptor返回的字典中的feature('attention' 或 'hidden')下的列表中元素的指标，不直接代表网络中实际的层数。**
  
  * 'feature' : feature(str) : 中间层的特征名，有效取值见 **FEATURES** 。可用的有：
  
    * 'attention' : 表示attention矩阵，大小应为 (batch_size, num_heads, length,length) 或 (batch_size, length, length)
    * 'hidden'：表示隐层输出，大小应为 (batch_size, length, hidden_dim)
  
  * 'loss' : loss(str) :损失函数的具体形式，有效取值见**MATCH_LOSS_MAP**的key。常用的有：
  
    * 'attention_mse'
    * 'attention_ce'
    * 'hidden_mse'
    * 'mmd'
    * ......
    
    每种损失的具体定义参见 **损失函数** 一节。
    
  * 'weight': weight (float) : 损失的权重
  
  * 'proj' : proj(List, optional) : 教师和学生的feature维度一样时，可选；不一样时，必选。为了匹配教师和学生中间层feature，所需要的投影函数。是一个列表，元素为：
  
    * proj[0] (str) :具体的转换函数，有效值见 **PROJ_MAP**。可用的有
      * 'linear_projection'
    * proj[1] (int):  转换函数的输入维度（学生侧的维度）
    * proj[2] (int):  转换函数的输出维度（教师侧的维度）
    * proj[3] (dict): 可选，转换函数的学习率等优化相关配置字典。如果不提供，linear_projection的学习率等优化器相关参数将采用optimzer的defaults配置，否则采用这里提供的参数。

**示例：**

```python
#最简单的配置：仅做最基本的蒸馏，用默认值即可，或尝试不同的temperature
distill_config = DistillationConfig(temperature=my_temperature)

#加入中间单层匹配的配置。
#此配置下，adaptor_T/S返回的字典results_T/S要包含'hidden'键。
#教师的 results_T['hidden'][10]和学生的results_S['hidden'][3]将计算hidden_mse loss
distill_config = DistillationConfig(
	temperature = 8,        #温度大于1通常能提升蒸馏效果
  intermediate_matches = [{'layer_T':10, 'layer_S':3, 'feature':'hidden','loss': 'hidden_mse', 'weight' : 1}]
)

#多层匹配。假设教师和学生的hidden dim分别为768和384，在学生和教师间增加投影（转换）函数
distill_config = DistillationConfig(
	temperature = 8, 
  intermediate_matches = [ \
    {'layer_T':0, 'layer_S':0, 'feature':'hidden','loss': 'hidden_mse', 'weight' : 1,'proj':['linear',384,768]},
    {'layer_T':4, 'layer_S':1, 'feature':'hidden','loss': 'hidden_mse', 'weight' : 1,'proj':['linear',384,768]},
    {'layer_T':8, 'layer_S':2, 'feature':'hidden','loss': 'hidden_mse', 'weight' : 1,'proj':['linear',384,768]},
    {'layer_T':12, 'layer_S':3, 'feature':'hidden','loss': 'hidden_mse', 'weight' : 1,'proj':['linear',384,768]}]
)
```

* (classmethod) **DistillConfig.from_json_file**(json_file : str) :
  * 从json文件读取配置

* (classmethod) **DistillConfig.from_dict**(dict_object : Dict) :
  * 从字典读取配置

## 蒸馏类

初始化某个蒸馏类后，使用其train方法开始训练。各个类的train方法的参数相同。

#### Distillation 

单模型单任务蒸馏推荐使用此类。

* class **Distillation**(**train_config**, **distill_config**, **model_T**, **model_S**, **adaptor_T**, **adaptor_S**, **custom_matches** = None):

  * train_config (TrainingConfig) : 训练配置
  * Distill_config (DistillationConfig)：蒸馏配置
  * model_T (torch.nn.Module)：教师模型
  * model_S (torch.nn.Module)：学生模型
  * custom_matches (List) : 如果预定义的match不满足需求，可通过custom_matches自定义
  * adaptor_T (Callable, function)：教师模型的adaptor
  * adaptor_S (Callable, function)：学生模型的adaptor

    * adatpor (batch, model_outputs) -> Dict：

  为适配不同模型的输入与输出，adaptor需要由用户提供。Adaptor是可调用的函数，接受两个输入，分别为batch （dataloader的输出）和model_outputs（模型的输出）。返回值为一个字典。见**变量与规范**中关于adaptor的说明。

  简单的adaptor的例子:

```python
'''
假设模型的输出为logits, sequence_output, total_loss:
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
def BertForGLUESimpleAdaptor(batch, model_outputs):
  return {'logits': (model_outputs[0],),
          'hidden': model.outputs[1],
          'inputs_mask': batch[1]}  # 模型返回了和ground-truth计算交叉熵得到的total_loss，但蒸馏时不打算使用该项，所以字典中可不加'losses'这一项
```

* Distillation.train(**optimizer**, **schduler**, **dataloader**, **num_epochs**,**call_back**, **\*\*args**)
  * optimizer: 优化器
  * schduler: 调整学习率，可以为None
  * dataloader: 数据集迭代器
  * num_epochs : 训练的轮数
  * callback: 回调函数，可以为None。在每个checkpoint会调用，调用方式为callback(model=self.model_S, step = global_step)。可用于在每个checkpoint做evaluation
  * \*\*args：额外的需要提供给模型的参数

调用模型过程说明：

* 如果batch是list或tuple，那么调用模型的形式为model(\*batch, \*\*args)。所以**请注意batch中各个字段的顺序和模型接受的顺序相匹配。**
* 如果batch是dict，那么调用模型的形式为model(\*\*batch,\*\*args)。所以**请注意batch中的key和模型接受参数名相匹配。**

#### BasicTraining

进行有监督训练，而非蒸馏。可用于调试，或训练教师模型。

* class **BasicTraining**(**train_config**, **model**, **adaptor**):
  * train_config (TrainingConfig) : 训练配置
  * model (torch.nn.Module)：待训练的模型
  * adaptor (Callable, function)：待训练的模型的adaptor
* BasicTraining.train 同 Distillation.train

#### BasicDistillation

提供最简单的soft-label+hard-label蒸馏方式，**不支持中间层特征匹配**。可作为调试或测试使用。

* class **BasicDIstillation** (**train_config**, **distill_config**, **model_T**, **model_S**, **adaptor_T**, **adaptor_S**):
  * train_config (TrainingConfig) : 训练配置
  * Distill_config (DistillationConfig)：蒸馏配置
  * model_T (torch.nn.Module)：教师模型
  * model_S (torch.nn.Module)：学生模型
  * adaptor_T (Callable, function)：教师模型的adaptor
  * adaptor_S (Callable, function)：学生模型的adaptor
* BasicDistillation.train 同 Distillation.train

#### BasicMultiTeacherDistillation

多教师蒸馏。将多个（同任务）教师模型蒸馏到一个学生模型上。**不支持中间层特征匹配**。

* class **BasicMultiTeacherDistillation** (**train_config**, **distill_config**, **model_T**, **model_S**, **adaptor_T**, **adaptor_S**):

  * train_config (TrainingConfig) : 训练配置
  * Distill_config (DistillationConfig)：蒸馏配置
  * model_T (List[torch.nn.Module])：教师模型的列表
  * model_S (torch.nn.Module)：学生模型
  * adaptor_T (Callable, function)：教师模型的adaptor
  * adaptor_S (Callable, function)：学生模型的adaptor

* BasicMultiTeacherDistillation.train 同 Distillation.train

## 例子

## 自定义

## 预定义列表/字典

预定义值在presets.py中：

1. **FEATURES**= ['hidden', 'attention']
   * intermediate_matches中的两类特征

2. **ADAPTOR_KEYS**  = ['logits', 'logits_mask', 'losses', 'inputs_mask'] + **FEATURES** 
   * adaptor会用到的keys

3. **PROJ_MAP**.keys() == ['linear'] 
   * projection的类型
     * 'linear' : 线性变换，#TODO

4. **MATCH_LOSS_MAP**.keys()==['attention_mse_sum', 'attention_mse', ‘attention_ce_mean', 'attention_ce', 'hidden_mse', 'cos', 'pkd', 'gram', 'mmd']
   * 预定义的损失函数

## 预定义损失函数

#### attention_mse

* 接收两个形状为 (**batch_size, num_heads, len, len**)的矩阵，计算两个矩阵间的mse损失。

* 如果提供了inputs_mask，mask掉padding位。

#### attention_mse_sum

* 接收两个矩阵，如果形状为(**batch_size, len, len**) ，直接计算两个矩阵间的mse损失；如果形状为 (**batch_size, num_heads, len, len**)，将num_heads维度求和，再计算两个矩阵间的mse损失。

* 如果提供了inputs_mask，mask掉padding位。

#### attention_ce

* 接收两个形状为 (**batch_size, num_heads, len, len**)的矩阵，取dim=-1为softmax的维度，计算两个矩阵间的交叉熵损失。

* 如果提供了inputs_mask，mask掉padding位。

#### attention_ce_mean

* 接收两个矩阵，如果形状为(**batch_size, len, len**) ，直接计算两个矩阵间的交叉熵损失；如果形状为 (**batch_size, num_heads, len, len**)，将num_heads维度求平均，再计算两个矩阵间的交叉熵损失。计算方式同**attention_ce** 。

* 如果提供了inputs_mask，mask掉padding位。

#### hidden_mse

* 接收两个形状为 (**batch_size, len, hidden_size**)的矩阵，计算两个矩阵间的mse损失。

* 如果提供了inputs_mask，mask掉padding位。

#### mmd

* 接收两个矩阵列表A和B，每个列表中包含两个形状为(**batch_size, len, hidden_size**)的矩阵。A中的矩阵的hidden_size和B中矩阵的hidden_size不必相同。计算A中的两个矩阵的相似度矩阵 ( (batch_size, len, len) ) 和B中的两个矩阵的相似度矩阵  ( (batch_size, len, len) ) 的mse损失。
* 如果提供了inputs_mask，mask掉padding位。
