import app


class QS3(object):


    def __init__(self, input=''):
        '''
        takes in a input description and split it into list of strings
        '''
        app.nltk.download('stopwords')
        app.nltk.download('punkt')
        self.update_vector_index()

    def update_vector_index(self):
        global VECTOR_INDEX

        stemmedList = [app.PS.stem(word) for word in app.LABEL_LIST]
        offset = 0
        # Associate a position with the keywords which maps to the dimension on the vector used to represent this word
        for word in stemmedList:
            app.VECTOR_INDEX[word] = offset
            offset += 1


    def set_label_list(self, labeal_list):
        '''
        Reset the whole label list
        '''
        global LABEL_LIST

        app.LABEL_LIST = list(dict.fromkeys(labeal_list))
        self.update_vector_index()


    def add_label_list(self, label_list):
        '''
        add new string into lable list
        '''
        global LABEL_LIST

        app.LABEL_LIST.append(list(dict.fromkeys(labeal_list)))
        self.update_vector_index()

    def query(self, in_q):

        input_vec = app.des_to_vector(in_q)
        app.update_table_integrity()
        return app.get_image_url(input_vec)


def main():
    print(app.LABEL_LIST)
    qs = QS3()
    img_list = qs.query('group labrador dog')
    print(type(img_list[0]))


if __name__ == '__main__':
    main()
