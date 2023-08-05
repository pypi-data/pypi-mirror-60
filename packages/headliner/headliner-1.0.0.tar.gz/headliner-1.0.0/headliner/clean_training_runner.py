from headliner.trainer import Trainer
from headliner.model.transformer_summarizer import TransformerSummarizer

data = [('You are the stars, earth and sky for me!', 'I love you.'),
        ('You are great, but I have other plans.', 'I like you.')]

summarizer = TransformerSummarizer(embedding_size=64, max_prediction_len=20)
trainer = Trainer(batch_size=2,
                  steps_per_epoch=100)
trainer.train(summarizer, data, num_epochs=2)
summarizer.save('/tmp/summarizer')

from headliner.model.transformer_summarizer import TransformerSummarizer

summarizer = TransformerSummarizer.load('/tmp/summarizer')
p = summarizer.predict('You are the stars, earth and sky for me!')
print(p)