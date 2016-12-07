#!/usr/bin/python

import math
import random
import logging

import os
import sys
import numpy as np;
import pandas as pd
import itertools;

import api
api.authenticate('adventurous-bandit-chieftains','11ddbaf3386aea1f2974eee984542152')


os.remove("ts.log")

logging.basicConfig(
		format='%(asctime)s, %(levelname)s: %(message)s',
		filename='ts.log',
		datefmt='%d-%m-%Y, %H:%M',
		level=logging.INFO)


if(sys.argv[1]=='--reset'):
	api.reset_leaderboard()


#headers = [5, 15, 35]
#languages = ['NL', 'EN', 'GE']
adtypes = ['skyscraper', 'square', 'banner']
colors = ['green', 'red', 'black', 'white']
prices = np.linspace(20.0, 40.0, 5)

colordf = pd.DataFrame([[1]*len(colors)]*2, index=['alfa', 'beta'], columns = colors)
adtypedf = pd.DataFrame([[1]*len(adtypes)]*2, index=['alfa', 'beta'], columns = adtypes)
pricedf = pd.DataFrame([[1]*len(prices)]*2, index=['alfa', 'beta'], columns = prices)

cumulative_reward = 0
n = 10000

minid=5000
maxid=5010

for run_id in range(minid,maxid):

    for request_number in xrange(n):

        context = api.get_context(run_id, request_number)

        if ((request_number%100)==0):
            logging.info(str(run_id) + ', ' + str(request_number));

        lang = str(context['context']['language'])
        if(lang == 'Other'):
               lang = 'EN'

        if(context['context']['os'] in ['Android','iOS']):
            header = 5
        else:
            header = 35

	randval = []
	for c in colordf.columns:
		randval.append(np.random.beta(colordf[c][0],colordf[c][1]))
	color = colordf.columns[np.argmax(randval)]
            
	randval = []
	for c in adtypedf.columns:
		randval.append(np.random.beta(adtypedf[c][0],adtypedf[c][1]))
	adtype = adtypedf.columns[np.argmax(randval)]
            
	randval = []
	for c in pricedf.columns:
		randval.append(np.random.beta(pricedf[c][0],pricedf[c][1]))
	price = pricedf.columns[np.argmax(randval)]
        
	result = api.serve_page(run_id, request_number,
                                header=header,
                                language=lang,
                                adtype=adtype,
                                color=color,
                                price=price)

        #print result, offer[4] * result['success']

	if(result['success']):
		colordf[color]['alfa'] += 1
		adtypedf[adtype]['alfa'] += 1
		pricedf[price]['alfa'] += 1
	else:
		colordf[color]['beta'] += 1
		adtypedf[adtype]['beta'] += 1
		pricedf[price]['beta'] += 1

        cumulative_reward += price * result['success']

    mean_reward = cumulative_reward / (n*((run_id+1)-minid))
    logging.info('Mean reward: %2f euro' % mean_reward)
