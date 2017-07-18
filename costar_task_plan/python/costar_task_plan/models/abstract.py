
import keras.optimizers as optimizers

class AbstractAgentBasedModel(object):
    '''
    In CTP, models are trained based on output from a particular agent --
    possibly the null agent (which would just load a dataset). The Agent class
    will also provide the model with a way to collect data or whatever.
    '''

    def __init__(self, lr=1e-4, epochs=1000, iter=1000, batch_size=32,
            clipnorm=100, show_iter=0, pretrain_iter=5,
            optimizer="sgd", model_descriptor="model", zdim=16, features=None,
            task=None, robot=None, *args,
            **kwargs):
        self.lr = lr
        self.iter = iter
        self.show_iter = show_iter
        self.pretrain_iter = pretrain_iter
        self.noise_dim = zdim
        self.epochs = epochs
        self.batch_size = batch_size
        self.optimizer = optimizer
        self.model_descriptor = model_descriptor
        self.task = task
        self.features = features
        self.robot = robot
        self.name = self.model_descriptor
        self.clipnorm = clipnorm
        if self.task is not None:
            self.name += "_%s"%self.task
        if self.features is not None:
            self.name += "_%s"%self.features
        
        # default: store the whole model here.
        # NOTE: this may not actually be where you want to save it.
        self.model = None

        print "================================================="
        print "Name =", self.name
        print "Features = ", self.features
        print "Robot = ", self.robot
        print "Task = ", self.task
        print "Model description = ", self.model_descriptor
        print "---------------------------"
        print "Iterations = ", self.iter
        print "Batch size =", self.batch_size
        print "[OPTIONAL] Epochs = ", self.epochs
        print "Show images every %d iter"%self.show_iter
        print "[OPTIONAL] Pretrain for %d iter"%self.pretrain_iter
        print "Noise dim = ", self.noise_dim
        print "---------------------------"
        print "Optimizer =", self.optimizer
        print "Learning Rate = ", self.lr
        print "Clip Norm = ", self.clipnorm
        print "================================================="

    def train(self, agent, *args, **kwargs):
        raise NotImplementedError('train() takes an agent.')

    def save(self):
        '''
        Save to a filename determined by the "self.name" field.
        '''
        if self.model is not None:
            self.model.save_weights(self.name + ".h5f")
        else:
            raise RuntimeError('save() failed: model not found.')

    def load(self):
        '''
        Load will use the current model descriptor and name to load the file
        that you are interested in, at least for now.
        '''
        raise NotImplementedError('load() not supported yet.')

    def _makeModel(self):
        '''
        Create the model based on some data set shape information.
        '''
        pass

    def getOptimizer(self):
        '''
        Set up a keras optimizer based on whatever settings you provided.
        '''
        optimizer = optimizers.get(self.optimizer)
        try:
            optimizer.lr = self.lr
            optimizer.clipnorm = self.clipnorm
        except Exception, e:
            print e
            raise RuntimeError('asdf')
        return optimizer
