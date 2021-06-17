from fairseq.models.bart import BARTModel

BASEDIR = 'models/JULIETT'
bart = BARTModel.from_pretrained(
        BASEDIR,
        checkpoint_file='checkpoint_best.pt',
        bpe='sentencepiece',
        sentencepiece_vocab=f'{BASEDIR}/sentence.bpe.mBART.model')
bart.eval()

sentence_list = ['operating country of w0301 ?']
translation = bart.sample(sentence_list, beam=5)
print(translation)
