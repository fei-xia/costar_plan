from __future__ import print_function

import numpy as np
from pypr.clustering import gmm
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class GMM(yaml.YAMLObject):
    '''
    Wraps some PyPr functions for easy grouping of different GMMs.
    Uses a couple different functions.
    '''

    yaml_tag = u'!GMM'

    def __init__(self, k=1, data=None, config=None, diag=1e-8, rawdata=None):
        if rawdata is not None:
            self.__dict__.update(rawdata)
        else:
            self.k = 1
            self.invsigma = [None] * k
            self.det = [None] * k

            if isinstance(data, np.ndarray):
                self.fit(data)
            elif not config == None:
                self.mu = config['mu']
                self.sigma = config['sigma']
                self.updateInvSigma()
                self.pi = config['pi']
                self.k = config['k']
            else:
                raise RuntimeError('Must provide either data array or config')

    def addNoise(self, noise):
        for i in range(len(self.sigma)):
            self.sigma[i] += noise * np.eye(self.sigma[i].shape[0])

    def updateInvSigma(self):
        for i in range(self.k):
            self.invsigma[i] = np.linalg.inv(self.sigma[i])
            #try:
            #    self.invsigma[i] = np.linalg.inv(self.sigma[i])
            #except np.linalg.linalg.LinAlgError, e:
            #    #print("ERROR: Inverse failed for cluster %d!" % i)
            #    #print(self.sigma[i])
            #    raise e


    def fit(self, data):
        '''
        fit gmm from data
        '''
        if self.k > 1:
            self.mu, self.sigma, self.pi, ll = gmm.em_gm(
                np.array(data), K=self.k)
        else:
            self.mu = [np.mean(data, axis=0)]
            self.sigma = [np.cov(data, rowvar=0)]
            self.pi = np.array([1.0])

        self.updateInvSigma()

        return self


    def score(self, data):
        '''
        return log likelihoods
        '''
        return gmm.gm_log_likelihood(data, self.mu, self.sigma, self.pi)

    def loglikelihood(self, data):
        # for i in range(k):
        i = 0
        ex1 = np.dot(self.invsigma[i], (data.T - self.mu[i]).T)
        ex = -0.5 * np.dot((data.T - self.mu[i]).T, ex1)
        return ex  # self.mu[0].transpose() * self.invsigma[0] * self.mu[0]


    def sample(self, nsamples=1):
        '''
        produce samples
        '''
        return gmm.sample_gaussian_mixture(self.mu, self.sigma, self.pi, nsamples)

    def predict(self, data):
        '''
        predict results by filling in NaNs
        '''
        p = gmm.predict(data, self.mu, self.sigma, self.pi)
        return data

    def dict(self):
        return {'mu': self.mu, 'sigma': self.sigma, 'pi': self.pi, 'k': self.k}
