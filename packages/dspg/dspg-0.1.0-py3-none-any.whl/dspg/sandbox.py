from wikidata import client

client = client.Client()
entity = client.get('Q223139')
film_poster = client.get('P3383')
image = client.get('P18')

print(entity[film_poster].image_url)