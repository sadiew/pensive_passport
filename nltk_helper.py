import wikipedia
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer

from model import City, WikipediaPage, Similarity, connect_to_db, db
from server import app
import psycopg2


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


def add_wiki_pages_to_db(city_ids):

	cities = [City.query.get(city_id) for city_id in city_ids]

	for city in cities:
		content = wikipedia.page(city.name).content
		wiki_page = WikipediaPage(city_id=city.city_id, content=content)
		db.session.add(wiki_page)

	db.session.commit()


def add_similarities_to_db(city_ids):

	combo_ids = ['%s-%s' %(city_ids[i], city_ids[j]) for i in range(len(city_ids)) 
													 for j in range(i+1,len(city_ids))]
	for combo_id in combo_ids:
		id1, id2 = combo_id.split("-")

		page1 = WikipediaPage.query.filter_by(city_id=id1).one()
		page2 = WikipediaPage.query.filter_by(city_id=id2).one()

		similarity_score = cosine_similarity(page1.content,page2.content)

		similarity = Similarity(combo_id=combo_id, city_id_1=id1, city_id_2=id2, similarity=similarity_score)
		db.session.add(similarity)

	db.session.commit()

# connect_to_db(app)
# city_ids = sorted([1417, 2012, 3218, 1195, 3358, 1705])
# add_wiki_pages_to_db(city_ids)
# add_similarities_to_db(city_ids)



