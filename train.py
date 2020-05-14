#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# machine learning imports
from simpletransformers.classification import ClassificationModel
import torch
import pandas as pd

# data collection and prep imports
import sqlite3
import newspaper
import requests
import random
import shutil
import sys
import os

# get the location of articles.db
def main():
	db = sys.argv[1]
	print(db)

	# grab a model, set it up for use for training
	cuda_available = torch.cuda.is_available()
	model_args = {
		'overwrite_output_dir': True
	}
	model = ClassificationModel(
	    "roberta", "roberta-base", use_cuda=cuda_available, args=model_args
	)

	# connect to the articles.db to grab any articles that have been rated
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	cursor.execute('select url, interesting from articles where read = 1')
	conn.commit()

	# Create a article object for each of the articles to be trained on TODO change this to an iterator later to preserve memory
	urls = [[newspaper.Article(item[0]), item[1]] for item in cursor.fetchall()]

	data = []
	for url in urls:
		try:
			req = requests.get(url[0].url)
			if req.status_code == requests.codes.ok:
				html = req.text
				data.append([newspaper.fulltext(html), url[1]])
		except Exception as e:
			print(e)
			continue

	random.shuffle(data)

	split = int(len(data) * .8)

	eval_data = data[split:]
	train_data = data[:split]

	print("train articles: ", len(train_data), " eval articles: ", len(eval_data))

	train_df = pd.DataFrame(train_data)
	train_df.columns = ["text", "labels"]

	eval_df = pd.DataFrame(eval_data)
	eval_df.columns = ["text", "labels"]


	print('made it to the training step!')
	model.train_model(train_df)

	result, model_outputs, wrong_predictions = model.eval_model(eval_df)

	print(result, model_outputs, wrong_predictions)

	cursor.execute('select id, url from articles where read = 0')
	conn.commit()

	unread_urls = [[newspaper.Article(item[1]), item[0]] for item in cursor.fetchall()]

	predictions_to_insert = []
	print(len(unread_urls))
	counter = len(unread_urls)
	for url in unread_urls:
		counter -=1
		print(counter, " stories left!")
		try:
			req = requests.get(url[0].url, timeout=1)
		except:
			continue
		if req.status_code == requests.codes.ok:
			html = req.text
			try:
				text = newspaper.fulltext(html)
			except Exception as e:
				print(e)
				continue

			predictions, raw_outputs = model.predict([text])
			print(predictions, type(raw_outputs[0][1]), url[1])
			prediction = [float(raw_outputs[0][1]), url[1]]
			print(prediction)	
			cursor.execute('update articles set inferred_interest = ? where id = ?;', prediction)
			conn.commit()

		else:
			print('issue with ', url[0].url)

	# delete the lock file
	os.remove('lock')
	print('lock removed')

	print('made all the predictions')

if __name__ == '__main__':
	main()


