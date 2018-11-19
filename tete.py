import pickle
import multiprocessing
import os

# with open('model_Decision_Tree.pkl', 'rb') as f:7
with open('model_Perceptron.pkl', 'rb') as f:
    a = pickle.load(f)

def classify(self, src_filename, sys_filename):
    assert self.model_step1
    assert self.model_step2

    self.stop = False
    src_lines = list()
    sys_lines = list()

    with open(src_filename, 'r') as _file:
        for line in _file:
            src_lines.append(line.split())

    with open(sys_filename, 'r') as _file:
        for line in _file:
            sys_lines.append(line.split())

    tagging_pool = multiprocessing.pool.Pool()
    tagging_result = None
    if not self.stop:
        tagging_result = tagging_pool.apply_async(self.tag_sentences,
                                                  args=(src_lines, sys_lines))
    tagging_pool.close()

    if not self.stop:
        alignments = self.align_sentences(src_filename, sys_filename)

    tagging_pool.join()
    if tagging_result is not None:
        tagged_lines = tagging_result.get()
    else:
        tagged_lines = list()

    result_classify = '#Sentencetypes src ref sys\n'
    result_classify += '#catfile lalic-catsv2\n'

    processing_list = list(zip(tagged_lines, alignments))
    chunksize = len(processing_list) // len(os.sched_getaffinity(0)) + 1
    pool = multiprocessing.pool.Pool()
    results = pool.map(classify_chunk,
                       processing_list,
                       chunksize=chunksize)

    return result_classify + '\n'.join(results)


def classify_chunk(instance):
    sent, alignment = instance
    return_blast = ''
    error_info = ''
    for sys_tw, src_tw in a.create_windows(sent[0], sent[1],
                                           alignment['alignment']):
        features = a.extract_features(sent,
                                      None, a.tw_size,
                                      ('test', (src_tw, sys_tw)))
        if features:
            data = a.format_features([features])

            # Ignore features which were not used in training
            extra_features = set(data.columns) - set(a.features)
            data = data.drop(extra_features, axis=1)

            # Include features which were not generated in test
            leftout_features = set(a.features) - set(data.columns)
            for f in leftout_features:
                data[f] = 0

            data = data[a.features]

            X = data.loc[:, data.columns != 'target']
            prediction_step1 = a.model_step1.predict(X)
            prediction_step1 = a.lb_step1.inverse_transform(prediction_step1)[0]
            if prediction_step1 != 'correct':
                prediction_step2 = a.model_step2.predict(X)
                prediction_step2 = a.lb_step2.inverse_transform(prediction_step2)[0]

                error_info += str(src_tw) + '#' + str(sys_tw) + '#-1#'
                error_info += prediction_step2 + ' '
    return_blast += ' '.join(alignment['src'])
    return_blast += '\n\n'
    return_blast += ' '.join(alignment['sys'])
    return_blast += '\n\n'
    return_blast += error_info
    return return_blast

ret = classify(a, '/home/marcio/SHARED/SHARED/Lalic/machine_translation/Corpus_FAPESP_v2/corpus_teste/en-pt/fapesp-v2.en-pt.test-a.en.atok',
               '/home/marcio/SHARED/SHARED/Lalic/machine_translation/Corpus_FAPESP_v2/corpus_teste/en-pt/MUSE-v2/fapesp-v2.en-pt.test-a.output')

print(ret)
