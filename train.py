# machine learning imports
from simpletransformers.classification import ClassificationModel
import torch

# data collection and prep imports
import sqlite3
import newspaper
import requests

# grab a model, set it up for use for training
cuda_available = torch.cuda.is_available()
model = ClassificationModel(
    "roberta", "roberta-base", use_cuda=cuda_available
)

# connect to the articles.db to grab any articles that have been rated
conn = sqlite3.connect('articles.db')
cursor = conn.cursor()
cursor.execute('select url, interesting from articles where read = 1')
conn.commit()

# Create a article object for each of the articles to be trained on TODO change this to an iterator later to preserve memory
urls = [[newspaper.Article(item[0]), item[1]] for item in cursor.fetchall()]

train_data = []
for url in urls:
	url[0].download
	url[0].parse
	html = requests.get(url[0].url).text
	print(newspaper.fulltext(html))
	train_data.append([url[0].text, url[1]])

print(len(train_data))

for line in train_data:
	print(line)



print('made it to the training step!')




