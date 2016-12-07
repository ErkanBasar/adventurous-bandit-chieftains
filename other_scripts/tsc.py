#!/usr/bin/python

import math
import random
import logging

import os
import sys
import numpy as np;
import pandas as pd
import itertools;

from scipy.stats import beta

import api
api.authenticate('adventurous-bandit-chieftains','11ddbaf3386aea1f2974eee984542152')


os.remove("tsc.log")

logging.basicConfig(
		format='%(asctime)s, %(levelname)s: %(message)s',
		filename='tsc.log',
		datefmt='%d-%m-%Y, %H:%M',
		level=logging.INFO)


if(len(sys.argv)>1 and sys.argv[1]=='--reset'):
	api.reset_leaderboard()


class BetaBandit(object):
    def __init__(self, num_options, prior=(1.0,1.0)):
        self.trials = np.zeros(shape=(num_options,), dtype=int)
        self.successes = np.zeros(shape=(num_options,), dtype=int)
        self.num_options = num_options
        self.prior = prior

    def add_result(self, trial_id, success):
        self.trials[trial_id] = self.trials[trial_id] + 1
        if (success):
            self.successes[trial_id] = self.successes[trial_id] + 1

    def get_recommendation(self, rn, rq):
        sampled_theta = []
        for i in range(self.num_options):
            #Construct beta distribution for posterior
            if(rn==1 and rg < 5001):
                dist = beta(1,1)
            else:
                dist = beta(self.prior[0]+self.successes[i],
                        self.prior[1]+self.trials[i]-self.successes[i])
            sampled_theta += [ dist.rvs() ]

        return sampled_theta.index( max(sampled_theta) )



#headers = [5, 15, 35]
#languages = ['NL', 'EN', 'GE']
adtypes = ['skyscraper', 'square', 'banner']
colors = ['green', 'red', 'black', 'white']
prices = np.linspace(20.0, 40.0, 5)

colorBB = BetaBandit(len(colors))
adtypeBB = BetaBandit(len(adtypes))
priceBB = BetaBandit(len(prices))

cumulative_reward = 0
n = 10000

minid=5000
maxid=5010

for run_id in range(minid,maxid):
    logging.info(str(run_id) + ': ');

    for request_number in xrange(n):

        context = api.get_context(run_id, request_number)

        if ((request_number%1000)==0):
		print(str(run_id) + ', ' + str(request_number))
		#logging.info(str(run_id) + ', ' + str(request_number));

        lang = str(context['context']['language'])
        if(lang == 'Other'):
               lang = 'EN'

        if(context['context']['os'] in ['Android','iOS']):
            header = 5
        else:
            header = 35

	iadtype = adtypeBB.get_recommendation(run_id, request_number)
	icolor = colorBB.get_recommendation(run_id, request_number)
	iprice = priceBB.get_recommendation(run_id, request_number)
        
	result = api.serve_page(run_id, request_number,
                                header=header,
                                language=lang,
                                adtype=adtypes[iadtype],
                                color=colors[icolor],
                                price=prices[iprice])

	colorBB.add_result(icolor, result['success'])
	adtypeBB.add_result(iadtype, result['success'])
	priceBB.add_result(iprice, result['success'])

        cumulative_reward += prices[iprice] * result['success']

    mean_reward = cumulative_reward / (n*((run_id+1)-minid))
    logging.info('Mean reward: %2f euro' % mean_reward)
