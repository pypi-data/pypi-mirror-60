import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

import sys, getopt

import pandas as pd

# pre-decided labels just for version 0.0.1
LABEL_LIST = ['animal', 'dog', 'husky', 'labrador', 'sky', 'beach', 'single', 'group']
VECTOR_INDEX = {}
PS = PorterStemmer()
IMAGE_LABEL_DF = pd.read_csv('https://image-storing.s3.us-east-2.amazonaws.com/test_url_sheet.csv')


def setup():
    print('--- start setup ...')
    nltk.download('stopwords')
    nltk.download('punkt')
    global LABEL_LIST
    global VECTOR_INDEX
    global IMAGE_LABEL_DF

    stemmedList = [PS.stem(word) for word in LABEL_LIST]
    offset = 0
    # Associate a position with the keywords which maps to the dimension on the vector used to represent this word
    for word in stemmedList:
        VECTOR_INDEX[word] = offset
        offset += 1

    if len(VECTOR_INDEX) > 0 and len(IMAGE_LABEL_DF) > 0:
        # print('vector_index:', VECTOR_INDEX)
        # print('image to label df:\n', IMAGE_LABEL_DF, '\n')
        print('--- setup complete')

def module_test():
    print('printing from module')

def des_to_vector(des):
    print('--- start des_to_vector ...')
    # remove stop words
    word_tokens = word_tokenize(des)
    stop_words = set(stopwords.words('english'))
    keyword_list = [w for w in word_tokens if w not in stop_words]
    stemmed_keyword_list = [PS.stem(w) for w in keyword_list]
    # to_vector
    return label_to_vector(stemmed_keyword_list)


def label_to_vector(label_list):
    input_vect = [0] * (len(VECTOR_INDEX))
    for w in label_list:
        i = VECTOR_INDEX[w]
        input_vect[i] = 1
    return input_vect


def update_table_integrity():
    global IMAGE_LABEL_DF

    vector_list = []
    for id, row in IMAGE_LABEL_DF.iterrows():
        vector_list.append(des_to_vector(row['label'].replace(',', ' ')))
    IMAGE_LABEL_DF['vector'] = vector_list


def cos_sim(a_vect, b_vect):
    len_a = sum(av*av for av in a_vect) ** 0.5
    len_b = sum(bv*bv for bv in b_vect) ** 0.5
    dot = sum(av*bv for av, bv in zip(a_vect, b_vect))
    return dot / (len_a * len_b)


def get_image_url(input_vec):
    print('--- getting url by cosine similarity')
    url_to_sim = []
    for id, row in IMAGE_LABEL_DF.iterrows():
        if round(cos_sim(row['vector'], input_vec), 5) == 1:
            url_to_sim.append(row['url'])
    return url_to_sim

# def main(argv):
#     print('--- START')
#
#     # options for running label_query_s3.0.0.1
#     # -h show help
#     # -s takes an english description of the image
#
#     description = []
#     try:
#         opts, args = getopt.getopt(argv, "hs")
#         # print('opts:', opts)
#         # print('args:', args)
#     except getopt.GetoptError:
#         print('Invalid Argument Usage. Try run with -h for help')
#         sys.exit(2)
#     if not opts:
#         raise ValueError('Invalid Argument Usage. Try run with -h for help')
#
#     for opt, arg in opts:
#         if opt == '-h':
#             print('app.py -s [ English description of the image ]')
#             sys.exit()
#         elif opt == '-s':
#             description = ' '.join(args)
#             setup()
#             input_vec = des_to_vector(description)
#             # print('index list: ', input_vec)
#             print('--- description now vectorized')
#             update_table_integrity()
#             print('--- IMAGE_LABEL_DF now with entry vector')
#             # print(IMAGE_LABEL_DF)
#             print('--- =====================================')
#             print('--- get image urls: \n\n', get_image_url(input_vec))
#             print('--- =================DONE================')
#
#
#
# if __name__ == '__main__':
#     main(sys.argv[1:])
