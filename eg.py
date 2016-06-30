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


os.remove("eg.log")

logging.basicConfig(
		format='%(asctime)s, %(levelname)s: %(message)s',
		filename='eg.log',
		datefmt='%d-%m-%Y, %H:%M',
		level=logging.INFO)


if(len(sys.argv)>1 and sys.argv[1]=='--reset'):
    api.reset_leaderboard()

def ind_max(x):
    m = max(x)
    return x.index(m)

class EpsilonGreedy():
    def __init__(self, epsilon, counts, values):
        self.epsilon = epsilon
        self.counts = counts
        self.values = values
        return

    def initialize(self, n_arms):
        self.counts = [0 for col in range(n_arms)]
        self.values = [0.0 for col in range(n_arms)]
        return

    def select_arm(self):
        if random.random() > self.epsilon:
            return ind_max(self.values)
        else:
            return random.randrange(len(self.values))
  
    def update(self, chosen_arm, reward):
        self.counts[chosen_arm] = self.counts[chosen_arm] + 1
        n = self.counts[chosen_arm]
    
        value = self.values[chosen_arm]
        new_value = ((n - 1) / float(n)) * value + (1 / float(n)) * reward
        self.values[chosen_arm] = new_value
        return

class UCB2(object):
    def __init__(self, alpha, counts, values):
        """
        UCB2 algorithm. Implementation of the slides at:
        http://lane.compbio.cmu.edu/courses/slides_ucb.pdf
        """
        self.alpha = alpha
        self.counts = counts
        self.values = values
        self.__current_arm = 0
        self.__next_update = 0
        return
  
    def initialize(self, n_arms):
        self.counts = [0 for col in range(n_arms)]
        self.values = [0.0 for col in range(n_arms)]
        self.r = [0 for col in range(n_arms)]
        self.__current_arm = 0
        self.__next_update = 0
  
    def __bonus(self, n, r):
        tau = self.__tau(r)
        bonus = math.sqrt((1. + self.alpha) * math.log(math.e * float(n) / tau) / (2 * tau))
        return bonus
  
    def __tau(self, r):
        return int(math.ceil((1 + self.alpha) ** r))
  
    def __set_arm(self, arm):
        """
        When choosing a new arm, make sure we play that arm for
        tau(r+1) - tau(r) episodes.
        """
        self.__current_arm = arm
        self.__next_update += max(1, self.__tau(self.r[arm] + 1) - self.__tau(self.r[arm]))
        self.r[arm] += 1

    def select_arm(self):
        n_arms = len(self.counts)

        # play each arm once
        for arm in range(n_arms):
            if self.counts[arm] == 0:
                self.__set_arm(arm)
                return arm

        # make sure we aren't still playing the previous arm.
        if self.__next_update > sum(self.counts):
            return self.__current_arm

        ucb_values = [0.0 for arm in range(n_arms)]
        total_counts = sum(self.counts)
        for arm in xrange(n_arms):
            bonus = self.__bonus(total_counts, self.r[arm])
            ucb_values[arm] = self.values[arm] + bonus

        chosen_arm = ind_max(ucb_values)
        self.__set_arm(chosen_arm)
        return chosen_arm

    def update(self, chosen_arm, reward):
        self.counts[chosen_arm] = self.counts[chosen_arm] + 1
        n = self.counts[chosen_arm]

        value = self.values[chosen_arm]
        new_value = ((n - 1) / float(n)) * value + (1 / float(n)) * reward
        self.values[chosen_arm] = new_value


#headers = [5, 15, 35]
#languages = ['NL', 'EN', 'GE']
adtypes = ['skyscraper', 'square', 'banner']
colors = ['green', 'red', 'black', 'white']
prices = [25.0, 30.0, 35.0, 40.0]

arms = list(itertools.product( adtypes, colors, prices))

#bandit = UCB2(0.2, None, None)
bandit = EpsilonGreedy(0.15, None, None)
#bandit.initialize(len(arms))

cumulative_reward = 0
n = 10000

minid=10000
maxid=10010

for run_id in range(minid,maxid):

    bandit.initialize(len(arms))

    for request_number in xrange(n):

        context = api.get_context(run_id, request_number)

        if ((request_number%1000)==0):
            print(str(run_id) + ', ' + str(request_number));

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
    print 'Mean reward: %2f euro' % mean_reward
