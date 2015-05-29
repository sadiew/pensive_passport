import wikipedia
from nltk import word_tokenize, pos_tag, FreqDist
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer

def create_stems(tokens):
	stemmer = PorterStemmer()
	stemmed_tokens = [stemmer.stem(token) for token in tokens]
	
	return stemmed_tokens

def generate_stemmed_tokens(page_content):
	lowered = page_content.lower()
	tokenizer = RegexpTokenizer(r'\w+')
	tokens = tokenizer.tokenize(lowered)
	stems = create_stems(tokens)
	
	return stems

def cosine_similarity(city1_content, city2_content):
	"""Determines the tf-idf (term frequency-inverse document frequency) and then
	calculates the cosine similarity between between the two Wikipedia pages."""

	vectorizer = TfidfVectorizer(tokenizer=generate_stemmed_tokens, stop_words='english')
	tfidf = vectorizer.fit_transform([city1_content, city2_content])
	return ((tfidf * tfidf.T).A)[0,1]

cities = ['Paris', 'Rome', 'Stockholm', 'Copenhagen', 'London', 'Istanbul', 'Budapest', 'Florence']
city_combos = []
city_content = {city:wikipedia.page(city).content for city in cities}

for i in range(len(cities)):
	for j in range(i+1,len(cities)):
		city_combos.append((cities[i], cities[j]))

cos_similarities = {combo[0]+'/'+combo[1]:cosine_similarity(city_content[combo[0]],city_content[combo[1]]) for combo in city_combos}
print cos_similarities