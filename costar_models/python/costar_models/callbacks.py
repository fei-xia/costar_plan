from __future__ import print_function

import os
import keras
import matplotlib.pyplot as plt
import numpy as np

class PredictorShowImage(keras.callbacks.Callback):
    '''
    Save an image showing what some number of frames and associated predictions
    will look like at the end of an epoch.
    '''
    directory = os.path.expanduser("~/.costar/debug")

    def __init__(self, predictor, features, targets,
            num_hypotheses=4,
            verbose=False,
            min_idx=0, max_idx=66, step=11):
        '''
        Set up a data set we can use to output validation images.

        Parameters:
        -----------
        predictor: model used to generate predictions
        targets: training target info, in compressed form
        num_hypotheses: how many outputs to expect
        verbose: print out extra information
        '''
        self.verbose = verbose
        self.predictor = predictor
        self.idxs = range(min_idx, max_idx, step)
        self.num = len(self.idxs)
        self.features = [f[self.idxs] for f in features]
        self.targets = [t[self.idxs] for t in targets]
        self.epoch = 0
        self.num_hypotheses = num_hypotheses
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def on_epoch_end(self, epoch, logs={}):
        # take the model and print it out
        self.epoch += 1
        imglen = 64*64*3
        img = self.targets[0][:,:imglen]
        img = np.reshape(img, (self.num,64,64,3))
        data, arms, grippers, label = self.predictor.predict(self.features)
        if self.verbose:
            print("============================")
        for j in range(self.num):
            name = os.path.join(self.directory,
                    "predictor_epoch%d_result%d.png"%(self.epoch,j))
            if self.verbose:
                print("----------------")
                print(name)
            fig = plt.figure(figsize=(3+int(1.5*self.num_hypotheses),2))
            plt.subplot(1,2+self.num_hypotheses,1)
            plt.title('Input Image')
            plt.imshow(self.features[0][j])
            plt.subplot(1,2+self.num_hypotheses,2+self.num_hypotheses)
            plt.title('Observed Goal')
            plt.imshow(img[j])
            for i in range(self.num_hypotheses):
                if self.verbose:
                    print("Arms = ", arms[j][i])
                    print("Gripper = ", grippers[j][i])
                    print("Label = ", np.argmax(label[j][i]))
                plt.subplot(1,2+self.num_hypotheses,i+2)
                plt.imshow(np.squeeze(data[j][i]))
                plt.title('Hypothesis %d'%(i+1))
            fig.savefig(name, bbox_inches="tight")
            if self.verbose:
                print("Arm/gripper target = ", self.targets[0][j,imglen:imglen+7])
                print("Label target = ", np.argmax(self.targets[0][j,(imglen+7):]))
            plt.close(fig)
