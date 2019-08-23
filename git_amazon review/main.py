from flask import request, render_template, Flask
import pandas as pd
import tempfile

import re
import nltk
nltk.download('stopwords')
from nltk import everygrams
from collections import Counter
from nltk.corpus import stopwords

def count_words(s, n_gram_min, n_gram_max, nb_words):
    stop_words = set(stopwords.words("english"))
    l_w = ['aren',"aren't","couldn'",'couldn',"couldn't",'didn',"didn't",'doesn',"doesn't",'don',"don't","hadn't",'hasn',
           "hasn't",'isn',"isn't",'mightn',"mightn't",'mustn',"mustn't",'needn',"needn't",'no','nor','not',"shan't",'shouldn',
           "shouldn't",'wasn',"wasn't","won't",'wouldn',"wouldn't"]
    for i in l_w:
        stop_words.discard(i)
    s = s.lower()
    s = re.sub(r'[^a-zA-Z0-9\s]', ' ', s)
    tokens = [token for token in s.split(" ") if token != ""]
    filtered_sentence = [] 
    for w in tokens: 
        if w not in stop_words: 
            filtered_sentence.append(w)
    output = list(everygrams(filtered_sentence, n_gram_min, n_gram_max))
    c = Counter(output)
    counts = c.most_common(nb_words)
    return counts
    

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("home.html")

@app.route("/result", methods = ["GET", "POST"])
def result():
    if request.files:
        data = request.files["file"]
    
    tempfile_path = tempfile.NamedTemporaryFile().name
    data.save(tempfile_path)
    df = pd.read_excel(tempfile_path)
    
    n_word = request.form.get('n_word', type=int)
    n_raw = request.form.get('n_raw', type=int)
    data = df.iloc[:,[3, 6]]
    for i in range(0, data.shape[0]):
        if data.at[i,'Review Rating'] > 3:
            data.at[i,'Score'] = 1
        elif data.at[i,'Review Rating'] < 4:
            data.at[i,'Score'] = 0
    data = data.drop(['Review Rating'], axis = 1)
    data_bad = data.loc[data['Score'] == 0]
    data_good = data.loc[data['Score'] == 1]
    bad_reviews = ''
    for x in data_bad['Review Text']:
        bad_reviews = bad_reviews + str(x)
    good_reviews = ''
    for i in data_good['Review Text']:
        good_reviews = good_reviews + str(i)
    count_bad_words_reviews = count_words(bad_reviews, n_word, n_word, n_raw)
    count_good_words_reviews = count_words(good_reviews, n_word, n_word, n_raw)
    
    
    return render_template("result.html", result1 = count_bad_words_reviews, result2 = count_good_words_reviews)


if __name__ == '__main__':
	app.run(debug=True)
    
    
    
    
