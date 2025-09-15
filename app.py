import requests, json

global_headers = {
    "Accept": "application/ld+json; charset=utf-8'"
}

def get_user(user_name: str) -> dict:
    split= user_name.split("@")
    user, instance = split[1], split[-1]

    finger = f"https://{instance}/.well-known/webfinger?resource=acct:{user}@{instance}"

    finger_result = json.loads(requests.get(finger).text)
    links = finger_result["links"]
    actor_url = None
    for link in links:
        if link["rel"] == "self":
            actor_url = link["href"]
            break
    
    actor_object = json.loads(requests.get(actor_url, headers=global_headers).text)

    actor_outbox = actor_object["outbox"]
    outbox_object = json.loads(requests.get(actor_outbox, headers=global_headers).text)

    first_index = int(outbox_object["first"].split("?page=")[-1])
    last_index = int(outbox_object["last"].split("?page=")[-1]) + 1

    reviews = list()

    for index in range(first_index, last_index):
        outbox_page_url = f"{actor_outbox}?page={index}"
        print(outbox_page_url)
        outbox = json.loads(requests.get(outbox_page_url, headers=global_headers).text)

        for item in outbox["orderedItems"]:
            if item["type"] != "Article": continue
            if "inReplyToBook" not in item: continue

            book_url = item["inReplyToBook"]
            book_response = requests.get(book_url, headers=global_headers)
            book_object = book_response.json()

            title = book_object["title"]

            languages = book_object["languages"]
            series = book_object["series"]
            image = book_object["cover"]["url"]
            isbn = book_object["isbn13"]
            date = f"#{item['published'].split('T')[0].replace('-', '/')}"
            
            review = item["content"]

            obsidian_book = {
                "title": title,
                "languages": languages,
                "series": series,
                "image": image,
                "isbn": isbn,
                "date": date,
                "authors": list(),
                "review": review
            }

            author_urls = book_object["authors"]

            for author_url in author_urls:
                author_object = json.loads(requests.get(author_url, headers=global_headers).text)
                obsidian_book["authors"].append(author_object["name"])

            reviews.append(obsidian_book)

    for review in reviews:
        print(review["title"])

        


if __name__ == "__main__":
    get_user("@mvrkws@bookwyrm.social")