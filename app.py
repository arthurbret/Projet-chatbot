from flask import Flask, render_template, request, session
import requests
import json


headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJlNjlmOGI2YzVjMWRmZWFiMjZhOGFkZjQ2YmQ4OTljMiIsInN1YiI6IjY2MTNjNjQ4OWJjZDBmMDE3ZDJiMGNiNyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.kz2PlUv4lC3munAlJxnZpGXOR4XDPJ4XNvDvfQ93YD4"
}


url = f"https://api.themoviedb.org/3/search/movie"

def ask_question(question):
    print(question)
    return input("> ")


def search_movies(query):
    params = {
        "query": query,
        "language": "fr-FR"
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        #print(response.json)
        return response.json()["results"]
    else:
        return None


def get_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=fr-FR"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_movie_genres(movie_id):
    movie_details = get_movie_details(movie_id)
    if movie_details and 'genres' in movie_details:
        return [genre['id'] for genre in movie_details['genres']]
    else:
        return None



def get_recommendations(favorite_movie_id, liked_movie_id, disliked_movie_id):
    # Headers nécessaires pour accéder à l'API de themoviedb
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJlNjlmOGI2YzVjMWRmZWFiMjZhOGFkZjQ2YmQ4OTljMiIsInN1YiI6IjY2MTNjNjQ4OWJjZDBmMDE3ZDJiMGNiNyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.kz2PlUv4lC3munAlJxnZpGXOR4XDPJ4XNvDvfQ93YD4"
    }

    # Fonction pour récupérer les recommandations en fonction de l'ID du film
    def get_movie_recommendations(movie_id):
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations"
        response = requests.get(url, headers=headers)
        data = response.json()
        return data['results'] if 'results' in data else []

    # Récupérer les recommandations pour les films aimés et non aimés
    recommendations = []
    for movie_id in [favorite_movie_id, liked_movie_id]:
        recommendations.extend(get_movie_recommendations(movie_id))

    # Filtrer les recommandations pour enlever les films non aimés
    recommendations = [movie for movie in recommendations if movie['id'] != disliked_movie_id]

    # Trier les recommandations par popularité, avis et imprévisibilité
    sorted_recommendations = sorted(recommendations, key=lambda x: (x['popularity'], x['vote_average']), reverse=True)

    # Récupérer les 3 premières recommandations (les plus populaires, les mieux notées et les moins prévisibles)
    top_popular = sorted_recommendations[0] if sorted_recommendations else None
    top_rated = sorted(recommendations, key=lambda x: x['vote_average'], reverse=True)[0] if recommendations else None
    most_unlikely = sorted(recommendations, key=lambda x: x['popularity'])[0] if recommendations else None

    return [top_popular, top_rated, most_unlikely]


def display_movies(movies):
    print("Voici les films trouvés :")
    for i, movie in enumerate(movies, 1):
        print(f"{i}. {movie['title']} ({movie['release_date']})")


def choose_movie(movies):
    while True:
        choice = ask_question("Sélectionne le numéro du film que tu veux voir (ou tape '0' pour annuler) :")
        if choice.isdigit():
            choice = int(choice)
            if 0 <= choice <= len(movies):
                return movies[choice - 1] if choice != 0 else None
        print("Choix invalide. Veuillez sélectionner un numéro de film valide.")




def display_movie_details(movie):
    print("\nDétails du film :")
    print(f"Titre : {movie['title']}")
    print(f"Date de sortie : {movie['release_date']}")
    print(f"Synopsis : {movie['overview']}")
    print(f"Note moyenne : {movie['vote_average']}")
    print(f"Nombre de votes : {movie['vote_count']}")

app = Flask(__name__)

favorite_movies = None
favorite_movie = None
liked_movies = None
liked_movie = None
disliked_movies = None
disliked_movie = None


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/userMessage', methods=['POST'])
def userMessage():
    data = request.get_json()
    reponse = data.get('message')
    global favorite_movies
    global favorite_movie
    global liked_movies
    global liked_movie
    global disliked_movies
    global disliked_movie
    if data.get('step')== 1:
        favorite_movie_title = reponse
        favorite_movies = search_movies(favorite_movie_title)
        favorite_movies_json = json.dumps(favorite_movies)
        return favorite_movies_json

    if data.get('step')== 2:
        choice = reponse
        if choice.isdigit():
            choice = int(choice)
            if 0 <= choice <= len(favorite_movies):
                favorite_movie = favorite_movies[choice - 1]
                choice = {"choice": choice}
                choice_json = json.dumps(choice)
                return choice_json
            else:
                invalide = {"invalide": "invalide"}
                invalide_json = json.dumps(invalide)
                return invalide_json
    if data.get('step')== 3:
        liked_movie_title = reponse
        liked_movies = search_movies(liked_movie_title)
        liked_movies_json = json.dumps(liked_movies)
        return liked_movies_json
    if data.get('step')== 4:
        choice = reponse
        if choice.isdigit():
            choice = int(choice)
            if 0 <= choice <= len(liked_movies):
                liked_movie = liked_movies[choice - 1]
                choice = {"choice": choice}
                choice_json = json.dumps(choice)
                return choice_json
            else:
                invalide = {"invalide": "invalide"}
                invalide_json = json.dumps(invalide)
                return invalide_json
    if data.get('step')== 5:
        disliked_movie_title = reponse
        disliked_movies = search_movies(disliked_movie_title)
        disliked_movies_json = json.dumps(disliked_movies)
        return disliked_movies_json
    if data.get('step')== 6:
        choice = reponse
        if choice.isdigit():
            choice = int(choice)
            if 0 <= choice <= len(disliked_movies):
                disliked_movie = disliked_movies[choice - 1]
                choice = {"choice": choice}
                choice_json = json.dumps(choice)
                return choice_json
            else:
                invalide = {"invalide": "invalide"}
                invalide_json = json.dumps(invalide)
                return invalide_json
    
    if data.get('step')==7:
        if favorite_movie and liked_movie and disliked_movie:
            recommendations = get_recommendations(favorite_movie['id'], liked_movie['id'], disliked_movie['id'])
            if recommendations:
                print(recommendations)
                recommendations_json = json.dumps(recommendations)
                return recommendations_json
            else:
                error_recommendation = {"recommendation": "not found"}
                error_recommendation_json = json.dumps(error_recommendation)
                return error_recommendation_json
        else:
            error_preferences = {"preferences": "not found"}
            error_preferences_json = json.dumps(error_preferences)
            return error_preferences_json



@app.route('/click')
def click():
    # Traitement de la requête HTTP
    # ...

    # Renvoi d'une réponse au client
    return 'Le bouton a été cliqué !'




#def main():
    print("Bienvenue au Chatbot de Recommandation de Films !")
    favorite_movie_title = ask_question("Quel est ton film préféré ?")
    favorite_movies = search_movies(favorite_movie_title)
    display_movies(favorite_movies)
    favorite_movie = choose_movie(favorite_movies)


    liked_movie_title = ask_question("Quel est un film que tu aimes bien ?")
    liked_movies = search_movies(liked_movie_title)
    display_movies(liked_movies)
    liked_movie = choose_movie(liked_movies)


    disliked_movie_title = ask_question("Quel est un film que tu n'aimes pas ?")
    disliked_movies = search_movies(disliked_movie_title)
    display_movies(disliked_movies)
    disliked_movie = choose_movie(disliked_movies)


    if favorite_movie and liked_movie and disliked_movie:
        recommendations = get_recommendations(favorite_movie['id'], liked_movie['id'], disliked_movie['id'])
        if recommendations:
            print("\nVoici trois films que tu pourrais aimer :")
            for movie in recommendations:
                display_movie_details(movie)
        else:
            print("Désolé, nous n'avons pas pu trouver de recommandations pour toi.")
    else:
        print("Désolé, certains films que tu as indiqués n'ont pas été trouvés.")


if __name__ == '__main__':
    app.run(debug=True)
