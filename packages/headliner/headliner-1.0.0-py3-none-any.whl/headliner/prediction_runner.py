import json
from sklearn.model_selection import train_test_split
from headliner.model.summarizer_bert import SummarizerBert

def read_data_json(file_path: str,
                   max_sequence_length: int):
    with open(file_path, 'r', encoding='utf-8') as f:
        data_out = json.load(f)
        return [d for d in zip(data_out['desc'], data_out['heads']) if len(d[0].split(' ')) <= max_sequence_length]



if __name__ == '__main__':

    train = read_data_json('/Users/cschaefe/datasets/welt_dedup.json', 400)
    train_data, val_data = train_test_split(train, test_size=100, shuffle=True, random_state=32)
    path_to_model = '/Users/cschaefe/Downloads/bert_model_newdata_nodrop_lowlr'
    summarizer = SummarizerBert.load(path_to_model)
    # summarizer.max_prediction_len = 30
    for val_index in range(100):
        text = val_data[val_index][0]
        target = val_data[val_index][1]
        print('(target) {}'.format(target))
        pred = summarizer.predict(text)
        print('(pred) {}'.format(pred))
