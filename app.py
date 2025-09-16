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

            review_id = item["id"]
            book_url = item["inReplyToBook"]
            book_response = requests.get(book_url, headers=global_headers)
            book_object = book_response.json()

            title = book_object["title"]

            sub_title = None
            if "subtitle" in book_object:
                sub_title = book_object["subtitle"]

            languages = book_object["languages"]
            series = book_object["series"]
            image = book_object["cover"]["url"]
            isbn = book_object["isbn13"]
            date = f"#{item['published'].split('T')[0].replace('-', '/')}"
            
            review = item["content"]

            obsidian_book = {
                "id": review_id,
                "title": title,
                "sub_title": sub_title,
                "url": book_url,
                "languages": languages,
                "series": series,
                "image": image,
                "isbn": isbn,
                "date": date,
                "authors": list(),
                "review": review,
                "serie": None
            }

            if "series" in book_object:
                if book_object["series"]:
                    obsidian_book["serie"] = book_object["series"]

            author_urls = book_object["authors"]

            for author_url in author_urls:
                author_object = json.loads(requests.get(author_url, headers=global_headers).text)
                obsidian_book["authors"].append(author_object["name"])

            write_file(obsidian_book)

    for review in reviews:
        print(review["title"])

    
def write_file(review: dict) -> None:
    full_title = review["title"]
    if review["sub_title"]:
        full_title = full_title + ": " + review["sub_title"]

    safe_file_name = full_title.replace(":", " -")
    print("Writing file", safe_file_name)

    with open(f"meldingar/{safe_file_name}.md", "w", encoding="utf8") as file:
        file.write("---\n")
        file.write(f"permalink: melding/bok/{full_title.lower().replace(':', '').replace(' ', '-')}\n")
        file.write(f"description: \"Melding av «{full_title}»\"\n")
        file.write(f"image: {review['image']}\n")
        file.write("fediverse:creator: \"@markus@skvip.lol\"\n")

        file.write("forfattar:\n")
        for author in review['authors']:
            file.write(f"- \"{author}\"\n")

        file.write(f"bookwyrm: {review['url']}\n")
        file.write(f"isbn: \"{review['isbn']}\"\n")

        file.write("språk:\n")
        for lang in review['languages']:
            file.write(f"- \"{lang}\"\n")

        if review['series']:
            file.write(f"serie: \"{review['serie']}\"\n")

        file.write("---\n")

        file.write(f"# {review['title']}\n")
        if review['sub_title']:
            file.write(f"## *{review['sub_title']}*\n\n")

        file.write(f"Dato: {review['date']}\n")
        file.write("Knagg: #melding/bok\n")
        file.write(f"Forfattar: ")
        for author in review["authors"]:
            file.write(f"[[{author}]] ")
        file.write("\n\n")

        file.write(f"[![Omslag til {review['title']}|100]({review['image']})]({review['url']})\n\n")

        file.write("## Kort skildring\n")
        file.write(f"*Dette er henta frå ein [bookwyrm-melding]({review['id']})*\n\n")

        file.write("## Melding\n")
        file.write(review['review'])
        file.write("\n")

        file.close()


if __name__ == "__main__":
    get_user("@mvrkws@bookwyrm.social")