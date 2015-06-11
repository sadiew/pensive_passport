from model import City, WikipediaPage, Similarity, db
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
import wikipedia


def get_user_similar_trips(city_id, user_id):
    """Query the DB for destinations searched by other users who searched
    the same 'winning' city."""

    query = """SELECT t.city_id,
                    c.name,
                    c.country,
                    COUNT(t.city_id)
            FROM trips AS t
                JOIN cities AS c on t.city_id = c.city_id
                JOIN searches AS s on t.search_id = s.search_id
            WHERE s.user_id IN
                (SELECT user_id
                FROM searches AS s
                JOIN trips AS t on s.search_id = t.search_id
                WHERE t.city_id = %s)
            AND t.city_id NOT IN
                (SELECT city_id
                FROM trips AS t
                JOIN searches AS s on t.search_id = s.search_id
                WHERE s.user_id = %s)
            GROUP BY 1,2,3
            ORDER BY COUNT(t.city_id) DESC
            LIMIT 4""" % (city_id, user_id)

    results = db.engine.execute(query)
    user_similar_cities = {result[0]: '%s, %s' % (result[1], result[2])
                           for result in results}

    return user_similar_cities


def get_nl_similar_trips(city_id, num_needed):
    """Look for cities with similar Wikipedia pages using cosine similarity."""

    similarities = check_for_nl_similarities(city_id, num_needed)

    if similarities:
        nltk_similar_cities = similarities

    else:
        add_wiki_page_to_db(city_id)
        add_similarities_to_db(city_id)
        nltk_similar_cities = check_for_nl_similarities(city_id, num_needed)

    return nltk_similar_cities


def add_wiki_page_to_db(city_id):

    city = City.query.get(city_id)

    content = wikipedia.page(city.name).content
    wiki_page = WikipediaPage(city_id=city.city_id, content=content)

    db.session.add(wiki_page)
    db.session.commit()


def add_similarities_to_db(city_id):

    results = db.session.query(WikipediaPage.city_id) \
        .filter(WikipediaPage.city_id != city_id).all()

    city_ids = [result[0] for result in results]

    combo_ids = ['%s-%s' % (city_id, city_ids[i])
                 for i in range(len(city_ids))]

    for combo_id in combo_ids:
        id1, id2 = combo_id.split("-")

        page1 = WikipediaPage.query.filter_by(city_id=id1).one()
        page2 = WikipediaPage.query.filter_by(city_id=id2).one()

        similarity_score = cosine_similarity(page1.content, page2.content)

        similarity = Similarity(combo_id=combo_id,
                                city_id_1=id1,
                                city_id_2=id2,
                                similarity=similarity_score)
        db.session.add(similarity)

    db.session.commit()


def check_for_nl_similarities(city_id, num_needed):

    query = """SELECT city_id_1, city_id_2
             FROM similarities
             WHERE (city_id_1 = %s OR city_id_2 = %s) and similarity > 0.3
             ORDER BY similarity DESC
             LIMIT %s;""" % (city_id, city_id, num_needed)

    results = db.engine.execute(query)

    if results:
        similar_cities = []
        for result in results:
            city_looking_for = result[1] if result[0] == int(city_id) else result[0]
            city = City.query.get(city_looking_for)
            similar_cities.append(city)

        nltk_similar_cities = {city.city_id: '%s, %s'
                               % (city.name, city.country)
                               for city in similar_cities}

        return nltk_similar_cities
    else:
        return None


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
    """Determines the tf-idf (term frequency-inverse document frequency)
    and then calculates the cosine similarity between between the two
    Wikipedia pages."""

    # remove 'stop words' that are too common and thus uninformative
    vectorizer = TfidfVectorizer(tokenizer=generate_stemmed_tokens,
                                 stop_words='english')
    tfidf = vectorizer.fit_transform([city1_content, city2_content])
    return ((tfidf * tfidf.T).A)[0, 1]
