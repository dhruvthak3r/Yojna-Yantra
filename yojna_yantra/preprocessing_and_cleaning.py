import json
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

with open('scheme_details.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'₹', 'rupees', text)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stopwords.words('english')]
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    preprocessed_text = ' '.join(tokens)
    return preprocessed_text

for scheme in data:
    scheme['details'] = preprocess_text(scheme.get('details', ''))
    scheme['benefits'] = preprocess_text(scheme.get('benefits', ''))
    scheme['eligibility'] = preprocess_text(scheme.get('eligibility', ''))
    scheme['application_process'] = preprocess_text(scheme.get('application_process', ''))
    scheme['documents_required'] = preprocess_text(scheme.get('documents_required', ''))

with open('preprocessed_scheme_details.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)