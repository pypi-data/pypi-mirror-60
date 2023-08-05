import json
from typing import Tuple, List

from sklearn.model_selection import train_test_split


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
    from headliner.trainer import Trainer
    from headliner.model.transformer_summarizer import TransformerSummarizer
    import tensorflow as tf
    train = read_data('/Users/cschaefe/datasets/en_ger.txt')

    train_data, val_data = train_test_split(train, test_size=100, shuffle=True, random_state=42)

    summarizer = TransformerSummarizer(embedding_size=128, num_layers=1, max_prediction_len=20)
    summarizer.optimizer = tf.keras.optimizers.Adam(learning_rate=5e-4)
    trainer = Trainer(batch_size=4, steps_per_epoch=500, steps_to_log=50, model_save_path='/tmp/summarizer',
                      tensorboard_dir='/tmp/tens/5e-4')
    trainer.train(summarizer, train_data, val_data=val_data, num_epochs=200)
