#!/usr/bin/python

import math
import random
import logging

import os
import sys
import numpy as np;
import itertools;

import api
api.authenticate('adventurous-bandit-chieftains','11ddbaf3386aea1f2974eee984542152')


os.remove("exp.log")

logging.basicConfig(
		format='%(asctime)s, %(levelname)s: %(message)s',
		filename='exp.log',
		datefmt='%d-%m-%Y, %H:%M',
		level=logging.INFO)


if(len(sys.argv)>1 and sys.argv[1]=='--reset'):
    api.reset_leaderboard()

def categorical_draw(probs):
  z = random.random()
  cum_prob = 0.0
  for i in range(len(probs)):
    prob = probs[i]
    cum_prob += prob
    if cum_prob > z:
      return i

  return len(probs) - 1

class Exp3():
  def __init__(self, gamma, weights):
    self.gamma = gamma
    self.weights = weights
    return
  
  def initialize(self, n_arms):
    self.weights = [1.0 for i in range(n_arms)]
    return
  
  def select_arm(self):
    n_arms = len(self.weights)
    total_weight = sum(self.weights)
    probs = [0.0 for i in range(n_arms)]
    for arm in range(n_arms):
      probs[arm] = (1 - self.gamma) * (self.weights[arm] / total_weight)
      probs[arm] = probs[arm] + (self.gamma) * (1.0 / float(n_arms))
    return categorical_draw(probs)
  
  def update(self, chosen_arm, reward):
    n_arms = len(self.weights)
    total_weight = sum(self.weights)
    probs = [0.0 for i in range(n_arms)]
    for arm in range(n_arms):
      probs[arm] = (1 - self.gamma) * (self.weights[arm] / total_weight)
      probs[arm] = probs[arm] + (self.gamma) * (1.0 / float(n_arms))
    
    x = reward / probs[chosen_arm]
    
    growth_factor = math.exp((self.gamma / n_arms) * x)
    self.weights[chosen_arm] = self.weights[chosen_arm] * growth_factor

#headers = [5, 15, 35]
#languages = ['NL', 'EN', 'GE']
adtypes = ['skyscraper', 'square', 'banner']
colors = ['green', 'red', 'black', 'white']
prices = [25.0, 30.0, 35.0, 40.0]

arms = list(itertools.product( adtypes, colors, prices))

bandit = Exp3(0.1,None)
bandit.initialize(len(arms))

cumulative_reward = 0
n = 10000

minid=5000
maxid=5001

for run_id in range(minid,maxid):

    for request_number in xrange(n):

        context = api.get_context(run_id, request_number)

        if ((request_number%100)==0):
            logging.info(str(run_id) + ', ' + str(request_number));

        offer_idx = bandit.select_arm();
        offer = arms[offer_idx];

        lang = str(context['context']['language'])
        if(lang == 'Other'):
               lang = 'EN'

        if(context['context']['os'] in ['Android','iOS']):
            header = 5
        else:
            header = 35

	price=offer[2]

        result = api.serve_page(run_id, request_number,
                                header=header,
                                language=lang,
                                adtype=offer[0],
                                color=offer[1],
                                price=price)

        #print result, offer[4] * result['success']

        bandit.update(offer_idx, price * result['success'])

        cumulative_reward += price * result['success']

    mean_reward = cumulative_reward / (n*((run_id+1)-minid))
    logging.info('Mean reward: %2f euro' % mean_reward)
