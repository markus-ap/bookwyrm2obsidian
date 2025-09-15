import requests, json

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
    
    actor_object = json.loads(requests.get(actor_url, headers={"Accept": "application/ld+json"}).text)

    actor_outbox = actor_object["outbox"]
    outbox_object = json.loads(requests.get(actor_outbox, headers={"Accept": "application/ld+json"}).text)

    first_index = int(outbox_object["first"].split("?page=")[-1])
    last_index = int(outbox_object["last"].split("?page=")[-1]) + 1

    reviews = list()

    for index in range(first_index, last_index):
        outbox_page_url = f"{actor_outbox}?page={index}"
        outbox = json.loads(requests.get(outbox_page_url, headers={"Accept": "application/ld+json"}).text)

        for item in outbox["orderedItems"]:
            if item["type"] != "Note": continue
            attachment = item["attachment"][0]
            
            book_url = item["tag"][0]["href"]
            book_object = json.loads(requests.get(book_url, headers={"Accept": "application/ld+json"}).text)

            title = book_object["title"]
            languages = book_object["languages"]
            series = book_object["series"]
            image = book_object["cover"]["url"]
            isbn = book_object["isbn13"]
            date = item["published"].split("T")[0]

            obsidian_book = {
                "title": title,
                "languages": languages,
                "series": series,
                "image": image,
                "isbn": isbn,
                "date": date,
                "authors": list()
            }

            author_urls = book_object["authors"]

            for author_url in author_urls:
                author_object = json.loads(requests.get(author_url, headers={"Accept": "application/ld+json"}).text)
                obsidian_book["authors"].append(author_object["name"])

            print(json.dumps(obsidian_book, indent=4))

            break
        break

        




if __name__ == "__main__":
    get_user("@mvrkws@bookwyrm.social")