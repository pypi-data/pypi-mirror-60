# AdaptNLP

[![build](https://circleci.com/gh/Novetta/adaptnlp.svg?style=shield&circle-token=ed777e78d54a959a2d7eef04f69510e25c46be27)](https://circleci.com/gh/Novetta/adaptnlp)

A high level framework for NLP tasks built on top of Zalando Research's Flair and Hugging Face's Transformers

## Quick Start

#### Requirements and Installation

##### Virtual Environment
To start a new python 3.6+ virtual environment, run this command:

```
python -m venv <name_of_venv_directory>
```

##### AdaptNLP Install
Clone the adaptnlp library from github and download from source.  This project is based on pytorch 0.4+ and python 3.6+

To install simply run this line in your virtual environment:
```
pip install adaptnlp
```

#### Introduction

Once you have installed adaptnlp, here are a few examples you can run:

##### Named Entity Recognition with `EasyTokenTagger`

```python
from adaptnlp import EasyTokenTagger

## Example Text
example_text = "Novetta's headquarters is located in Mclean, Virginia."

## Load the token tagger module and tag text with the NER model 
tagger = EasyTokenTagger()
sentences = tagger.tag_text(text=example_text, model_name_or_path="ner")

## Output tagged token span results in Flair's Sentence object model
for sentence in sentences:
    for entity in sentence.get_spans("ner"):
        print(entity)

```

##### English Sentiment Classifier `EasySequenceClassifier`

```python
from adaptnlp import EasySequenceClassifier 

## Example Text
example_text = "Novetta is a great company that was chosen as one of top 50 great places to work!"

## Load the sequence classifier module and classify sequence of text with the english sentiment model 
classifier = EasySequenceClassifier()
sentences = classifier.tag_text(text=example_text, model_name_or_path="en-sentiment")

## Output labeled text results in Flair's Sentence object model
for sentence in sentences:
    print(sentence.labels)

```

##### Span-based Question Answering `EasyQuestionAnswering`

```python
from adaptnlp import EasyQuestionAnswering 

## Example Query and Context 
query = "What is the meaning of life?"
context = "Machine Learning is the meaning of life."
top_n = 5

## Load the QA module and run inference on results 
qa = EasyQuestionAnswering()
best_answer, best_n_answers = qa.predict_bert_qa(query=query, context=context, n_best_size=top_n)

## Output top answer as well as top 5 answers
print(best_answer)
print(best_n_answers)

```

## Tutorials

Look in the tutorials directory for a quick introduction to the library and it's very simple
and straight forward use cases:

  1. Token Classification: NER, POS, Chunk, and Frame Tagging
  2. Sequence Classification: Sentiment
  3. Embeddings: Transformer Embeddings e.g. BERT, XLM, GPT2, XLNet, alBERTa
  4. Custom Fine-Tuning and Training
  
## Docker
Build docker image and run container with the following commands in the directory of the Dockerfile
to create a container with adaptnlp installed and ready to go

Note: A container with GPUs enabled requires Docker version 19.03+ and nvida-docker installed
```
docker build -t nnlp:latest .
docker run -it nnlp:latest bash
```
If you want to use CUDA compatible GPUs 
```
docker run -it --gpus all nnlp:latest bash
```

### License
Copyright (C) 2019 Novetta - All Rights Reserved 
 Unauthorized copying of this file, via any medium is strictly prohibited
 
 Author Andrew Chang achang@novetta.com, 2019 



