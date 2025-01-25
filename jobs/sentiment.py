""" Sentiment Analysis Module """
import tweetnlp

# GET DATASET (MULTILINGUAL)
for l in ['english', 'italian', 'japanese']:
    dataset_multilingual, label2id_multilingual = tweetnlp.load_dataset('sentiment', multilingual=True, task_language=l)

model = tweetnlp.load_model('sentiment', multilingual=True)

def get_sentiment(text):
    """ Sentiment analysis result """
    output = model.sentiment(text, return_probability=True)
    print(output)
    return output['label']
