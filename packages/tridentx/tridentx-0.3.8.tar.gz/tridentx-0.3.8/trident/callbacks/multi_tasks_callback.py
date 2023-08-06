
import os
import random
import warnings
import math
import numpy as np
from  ..callbacks import CallbackBase
from ..backend.common import *
from ..backend.load_backend import get_backend
from ..data.image_common import *
from ..misc.visualization_utils import *
if get_backend()=='pytorch':
    import torch
    import torch.nn as nn
    from ..backend.pytorch_backend import to_numpy,to_tensor
    from ..optims.pytorch_losses import CrossEntropyLoss,MSELoss
    from ..optims.pytorch_trainer import *
    from ..layers.pytorch_activations import *
elif get_backend()=='tensorflow':
    from ..backend.tensorflow_backend import  to_numpy,to_tensor
    from ..optims.tensorflow_losses import CrossEntropyLoss,MSELoss
    from ..optims.tensorflow_trainer import *
elif get_backend()=='cntk':
    from ..backend.cntk_backend import  to_numpy,to_tensor
    from ..optims.cntk_losses import CrossEntropyLoss,MSELoss
    from ..optims.cntk_trainer import *


__all__ = ['GanCallbacksBase', 'GanCallback']

class GanCallbacksBase(CallbackBase):
    def __init__(self):
        super(GanCallbacksBase, self).__init__(is_shared=True)

    pass


def pullaway_loss(embeddings):
    norm = torch.sqrt(torch.sum(embeddings ** 2, -1, keepdim=True))
    normalized_emb = embeddings / norm
    similarity = torch.matmul(normalized_emb, normalized_emb.transpose(1, 0))
    batch_size = embeddings.size(0)
    loss_pt = (torch.sum(similarity) - batch_size) / (batch_size * (batch_size - 1))
    return loss_pt




class GanCallback(GanCallbacksBase):

    def __init__(self,generator=None,discriminator=None,
                 gan_type='gan', label_smoothing=False,
                 noised_real=True,
                 weight_clipping=False,tile_image_frequency=100,
                 experience_replay=False,**kwargs):
        _available_gan_type=['gan','began','ebgan','wgan','wgan-gp','lsgan','rasgan']
        super(GanCallback, self).__init__()
        if isinstance(generator,ImageGenerationModel):
            self.generator=generator.model
        if isinstance(discriminator, ImageClassificationModel):
            self.discriminator=discriminator.model
        self.data_provider=None
        self.z_noise=None
        self.D_real=None
        self.D_fake = None
        self.img_real = None
        self.img_fake = None
        self.gan_type=gan_type if gan_type in _available_gan_type else None
        self.label_smoothing=label_smoothing
        self.noised_real=noised_real
        self.tile_image_frequency=tile_image_frequency
        self.weight_clipping=weight_clipping
        self.experience_replay=experience_replay
        if self.experience_replay==True:
            make_dir_if_need('Replay')
        self.tile_images=[]


    def on_training_start(self, training_context):
        training_items=training_context['training_items']
        self.data_provider=training_context['_dataloaders'].value_list[0]
        for training_item in training_items:
            if isinstance(training_item,ImageGenerationModel):
                if self.generator is None:
                    self.generator=training_item.model
                    training_context['generator'] = training_item.model
            elif isinstance(training_item,ImageClassificationModel):
                if self.discriminator is None:
                    self.discriminator = training_item.model
                    training_context['discriminator'] =training_item.model

    def on_data_received(self, training_context):
        model=training_context['current_model']
        current_mode=None
        if self.generator is not None and model.name ==self.generator.name :
            training_context['generator'] = model
            current_mode='generator'
        elif self.discriminator is not None and model.name ==self.discriminator.name:
            training_context['discriminator'] = model
            current_mode = 'discriminator'
        elif model.name ==  'generator':
            training_context['generator'] = model
            current_mode = 'generator'
        elif model.name == 'discriminator':
            training_context['discriminator'] = model
            current_mode = 'discriminator'

        if current_mode=='generator':
            self.z_noise=training_context['current_input']
            #training_context['z_noise']=self.z_noise
            curr_epochs=training_context['current_epoch']
            tot_epochs=training_context['total_epoch']
            self.img_real =training_context['current_target']

            #noise input
            if self.noised_real:
                self.img_real=training_context['current_target'] + to_tensor(0.2*(1-float(curr_epochs)/tot_epochs)*np.random.standard_normal(list(self.img_real.size())))
            #training_context['img_real'] =self.img_real
            #training_context['D_real'] = self.discriminator(self.img_real)
            self.D_real=self.discriminator(self.img_real)

            self.img_fake= self.generator(self.z_noise)
            # training_context['img_fake']=self.img_fake
            # training_context['D_fake'] =  self.discriminator(self.img_fake)
            self.D_fake=  self.discriminator(self.img_fake)

        elif current_mode=='discriminator':
            #training_context['img_real']=training_context['current_input']
            self.img_real =training_context['current_input']



    def post_loss_calculation(self, training_context):
        model = training_context['current_model']
        current_mode = None
        is_collect_data=training_context['is_collect_data']


        true_label=to_tensor(np.ones((self.D_real.size()),dtype=np.float32))
        false_label = to_tensor(np.zeros((self.D_real.size()), dtype=np.float32))

        if self.label_smoothing:
            if training_context['current_epoch']<20:
                true_label = to_tensor(np.random.randint(75,125,(self.D_real.size())).astype(np.float32)/100.0)
            elif training_context['current_epoch'] < 50:
                true_label = to_tensor(np.random.randint(80,120,(self.D_real.size())).astype(np.float32)/100.0)
            elif training_context['current_epoch'] < 200:
                true_label = to_tensor(np.random.randint(90,110,(self.D_real.size())).astype(np.float32)/100.0)
            else:
                pass
        true_label.requires_grad=False
        false_label.requires_grad=False
        if self.generator is not None and model.name == self.generator.name:
            self.generator=model
            self.img_fake =self.generator(self.z_noise)
            #training_context['img_fake'] = self.img_fake
            self.D_fake = self.discriminator(self.img_fake)
            #training_context['D_fake']=self.D_fake
            this_loss=0

            if self.gan_type=='gan':
                adversarial_loss = torch.nn.BCELoss()
                this_loss = adversarial_loss(self.D_fake, true_label).mean()
            elif self.gan_type == 'wgan':
                this_loss=-self.D_fake.mean()

            elif self.gan_type == 'wgan-gp':
                this_loss=-self.D_fake.mean()

            elif self.gan_type == 'lsgan':
                adversarial_loss = torch.nn.MSELoss()
                this_loss = adversarial_loss(self.D_fake, true_label)
            elif self.gan_type == 'rasgan':
                adversarial_loss = torch.nn.BCEWithLogitsLoss()
                D_r_tilde = sigmoid(self.D_real - self.D_fake.mean())
                D_f_tilde = sigmoid(self.D_fake - self.D_real.mean())
                this_loss =- torch.log(D_f_tilde + 1e-8).mean() -torch.log(1 - D_r_tilde + 1e-8).mean()


            training_context['current_loss'] = training_context['current_loss'] + this_loss
            if 'D_fake' not in training_context['tmp_metrics']:
                training_context['tmp_metrics']['D_fake'] = []
                training_context['metrics']['D_fake'] = []
            training_context['tmp_metrics']['D_fake'].append(to_numpy(self.D_fake).mean())

            if is_collect_data:
                if 'gan_g_loss' not in training_context['losses']:
                    training_context['losses']['gan_g_loss']=[]
                training_context['losses']['gan_g_loss'].append(float(to_numpy(this_loss)))



        elif self.discriminator is not None and model.name == self.discriminator.name:
            self.discriminator = model
            self.D_real=self.discriminator(self.img_real)
            self.D_fake = self.discriminator(self.img_fake)
            # training_context['D_real']=self.D_real
            # training_context['D_fake']=self.D_fake
            # training_context['discriminator'] = model
            this_loss = 0
            if self.gan_type == 'gan':
                adversarial_loss = torch.nn.BCELoss()
                real_loss = adversarial_loss(self.D_real, true_label)
                fake_loss = adversarial_loss(self.D_fake, false_label)
                this_loss = (real_loss + fake_loss).mean() / 2
            elif self.gan_type == 'wgan':
                this_loss =-self.D_real.mean()+ self.D_fake.mean()
            elif self.gan_type == 'wgan-gp':
                alpha = torch.rand(self.img_real.size(0), 1, 1, 1).cuda().expand_as(self.img_real)
                interpolated = alpha * self.img_real.data + (1 - alpha) * self.img_fake.data
                interpolated.requires_grad = True
                out = self.discriminator(interpolated)

                grad = torch.autograd.grad(outputs=out, inputs=interpolated, grad_outputs=torch.ones(out.size()).cuda(),
                                           retain_graph=True, create_graph=True, only_inputs=True)[0]
                grad = grad.view(grad.size(0), -1)
                grad_l2norm = torch.sqrt(torch.sum(grad ** 2, dim=1))

                this_loss = 10 * torch.mean((grad_l2norm - 1) ** 2) -self.D_real.mean() + self.D_fake.mean()

            elif self.gan_type == 'lsgan':
                adversarial_loss =torch.nn.MSELoss()
                real_loss = adversarial_loss(self.D_real, true_label)
                fake_loss = adversarial_loss(self.D_fake, false_label)
                this_loss = (real_loss + fake_loss) / 2
            elif self.gan_type=='rasgan':
                D_r_tilde = sigmoid(self.D_real - self.D_fake.mean())
                D_f_tilde = sigmoid(self.D_fake - self.D_real.mean())
                this_loss =- torch.log(D_r_tilde + 1e-8).mean() -torch.log(1 - D_f_tilde + 1e-8).mean()

            training_context['current_loss'] = training_context['current_loss'] + this_loss
            if 'D_real' not in training_context['tmp_metrics']:
                training_context['tmp_metrics']['D_real'] = []
                training_context['metrics']['D_real'] = []
            training_context['tmp_metrics']['D_real'].append(to_numpy(self.D_real).mean())

            if is_collect_data:
                if 'gan_d_loss' not in training_context['losses']:
                    training_context['losses']['gan_d_loss']=[]
                training_context['losses']['gan_d_loss'].append(float(to_numpy(this_loss)))

    def on_optimization_step_end(self, training_context):
        model = training_context['current_model']
        is_collect_data = training_context['is_collect_data']

        if self.generator is not None and model.name == self.generator.name:
            self.generator = model
            self.img_fake = self.generator(self.z_noise)
            if self.experience_replay and random.randint(0,100)%25==0:
                np.save('Replay/{0}.npy'.format(get_time_suffix()),to_numpy(self.img_fake))

            # training_context['img_fake'] = self.img_fake
            # self.D_fake = self.discriminator(self.img_fake)
            # training_context['D_fake'] = self.D_fake
            #
            # if self.gan_type == 'gan':
            #     adversarial_loss = torch.nn.BCELoss()
            #     this_loss = adversarial_loss(self.D_fake, true_label)
            # elif self.gan_type == 'wgan':
            #     this_loss = -self.D_fake.mean()


        elif self.discriminator is not None and model.name == self.discriminator.name:
            self.discriminator = model


            if self.gan_type == 'wgan' or self.weight_clipping:
                for p in self.discriminator.parameters():
                    p.data.clamp_(-0.01, 0.01)

            # self.D_real = self.discriminator(self.img_real)
            # self.D_fake = self.discriminator(self.img_fake)
            # training_context['D_real'] = self.D_real
            # training_context['D_fake'] = self.D_fake
            # training_context['discriminator'] = model

    def on_batch_end(self, training_context):
        model = training_context['current_model']
        if self.generator is not None and model.name == self.generator.name:
            if (training_context['current_epoch']*training_context['total_batch']+training_context['current_batch']+1)%self.tile_image_frequency==0:

                for i in range(3):
                    train_data=self.data_provider.next()
                    input = None
                    target = None
                    if 'data_feed' in training_context and len(training_context['data_feed']) > 0:
                        data_feed = training_context['data_feed']
                        input = to_tensor(train_data[data_feed.get('input')]) if data_feed.get('input') >= 0 else None
                        target = to_tensor(train_data[data_feed.get('target')]) if data_feed.get('target') >= 0 else None
                        imgs = to_numpy(self.generator(input)).transpose([0,2,3,1])*127.5+127.5
                        self.tile_images.append(imgs)


                # if self.tile_image_include_mask:
                #     tile_images_list.append(input*127.5+127.5)
                tile_rgb_images(*self.tile_images, save_path=os.path.join('Results', 'tile_image_{0}.png'), imshow=True)
                self.tile_images=[]

        elif self.discriminator is not None and model.name == self.discriminator.name:
            if training_context['current_epoch']>3 and self.gan_type not in ('wgan','wgan-gp'):
                if float(self.D_real.mean())>0.9 and float(self.D_fake.mean())<0.1:
                    training_context['stop_update']=True


    def on_epoch_end(self, training_context):
        model = training_context['current_model']
        if training_context['current_epoch']==9 or (training_context['current_epoch']>=9 and (training_context['current_epoch']+1)%20==0):
            if training_context['optimizer'].lr>1e-6:
                training_context['optimizer'].adjust_learning_rate(training_context['optimizer'].lr*0.5,True)









