""" Sentiment Analysis Module """
import asent # pylint: disable=unused-import
import spacy

def getSentiment(text):
    """ Sentiment analysis result """
    # load spacy pipeline
    nlp = spacy.load("en_core_web_lg")
    # add the rule-based sentiment model
    nlp.add_pipe("asent_en_v1")
    sentiment = nlp(text)
    #print(f"totale: {doc._.polarity.compound}")

    return sentiment._.polarity.compound
