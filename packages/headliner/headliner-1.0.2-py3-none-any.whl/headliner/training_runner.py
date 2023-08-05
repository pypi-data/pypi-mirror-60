import tensorflow as tf
import json
import logging
from typing import Tuple, List

from sklearn.model_selection import train_test_split
from spacy.lang.en import English
from tensorflow_datasets.core.features.text import SubwordTextEncoder
from transformers import BertTokenizer

from headliner.model.bert_summarizer import BertSummarizer
from headliner.preprocessing.bert_preprocessor import BertPreprocessor
from headliner.preprocessing.bert_vectorizer import BertVectorizer
from headliner.trainer import Trainer


def read_data_json(file_path: str,
                   max_sequence_length: int) -> List[Tuple[str, str]]:
    with open(file_path, 'r', encoding='utf-8') as f:
        data_out = json.load(f)
        return [d for d in zip(data_out['desc'], data_out['heads']) if len(d[0].split(' ')) <= max_sequence_length]


def read_data(file_path: str) -> List[Tuple[str, str]]:
    data_out = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for l in f.readlines():
            x, y = l.strip().split('\t')
            data_out.append((x, y))
        return data_out


if __name__ == '__main__':
    train = read_data('/Users/cschaefe/datasets/en_ger.txt')[0:10000]

    train_data, val_data = train_test_split(train, test_size=10, shuffle=True, random_state=42)
    logging.getLogger("transformers.tokenization_utils").setLevel(logging.ERROR)
    tokenizer_input = BertTokenizer.from_pretrained('bert-base-uncased')
    preprocessor = BertPreprocessor(nlp=English())
    train_prep = [preprocessor(t) for t in train_data]

    print(train_prep[:100])

    targets_prep = [t[1] for t in train_prep]
    tokenizer_target = SubwordTextEncoder.build_from_corpus(
        targets_prep, target_vocab_size=2 ** 13,
        reserved_tokens=[preprocessor.start_token, preprocessor.end_token])

    summarizer = BertSummarizer(num_heads=8,
                                num_layers_encoder=0,
                                num_layers_decoder=4,
                                feed_forward_dim=512,
                                embedding_size_encoder=768,
                                embedding_size_decoder=768,
                                bert_embedding_encoder='bert-base-uncased',
                                dropout_rate=0,
                                max_prediction_len=30)
    summarizer.optimizer_decoder = tf.keras.optimizers.Adam(learning_rate=1e-4)
    summarizer.optimizer_encoder = tf.keras.optimizers.Adam(learning_rate=2e-5)
    vectorizer = BertVectorizer(tokenizer_input, tokenizer_target)
    summarizer.init_model(preprocessor, vectorizer)

    trainer = Trainer(batch_size=4, steps_per_epoch=100, model_save_path='/tmp/summarizer_bert',
                      tensorboard_dir='/tmp/tfbert2')
    trainer.train(summarizer, train_data, val_data=val_data, num_epochs=200)
