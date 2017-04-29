import numpy as np
import tensorflow as tf
from keras.utils.data_utils import get_file
from utils import clean_text, build_vocab, convert_text_to_idx
from rnn_text_gen import RNNTextGen


BATCH_SIZE = 128
SEQ_LEN = 40
NUM_LAYER = 3
CELL_SIZE = 128
prime_texts = ['your desire to', 'it seems to me', 'there are']


if __name__ == '__main__':
    path = get_file('nietzsche.txt', origin='https://s3.amazonaws.com/text-datasets/nietzsche.txt')
    text = open(path).read().replace('\n', '')

    print('Cleaning Text')
    text = clean_text(text)
    all_word_list = list(text) # now we are doing char-level, use .split() for word-level

    print('Building Nietzsche Vocab by Characters')
    idx2word, word2idx = build_vocab(all_word_list)
    vocab_size = len(idx2word)
    print('Vocabulary Length = {}'.format(vocab_size))
    assert len(idx2word) == len(word2idx), "len(idx2word) is not equal to len(word2idx)" # sanity Check

    all_word_idx = convert_text_to_idx(all_word_list, word2idx)
    X = np.resize(all_word_idx, [int(len(all_word_idx)/SEQ_LEN), SEQ_LEN])
    print('X shape: ', X.shape)
    
    sess = tf.Session()
    with tf.variable_scope('training'):
        train_model = RNNTextGen(cell_size=CELL_SIZE, n_layers=NUM_LAYER,
                                 vocab_size=vocab_size, seq_len=SEQ_LEN,
                                 sess=sess)
    with tf.variable_scope('training', reuse=True):
        sample_model = RNNTextGen(cell_size=CELL_SIZE, n_layers=NUM_LAYER,
                                  vocab_size=vocab_size, seq_len=1,
                                  sess=sess)
    log = train_model.fit(X, n_epoch=25, batch_size=BATCH_SIZE,
                          en_exp_decay=True,
                          sample_pack=(sample_model, idx2word, word2idx, 20, prime_texts))
    