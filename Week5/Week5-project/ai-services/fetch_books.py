import os
import requests

# Your .NET API URL
API_URL = "http://localhost:5194/api/books"

# Folder where text documents will be stored
DOCUMENTS_FOLDER = "documents"

os.makedirs(DOCUMENTS_FOLDER, exist_ok=True)


def fetch_books():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching books: {e}")
        return []


def create_documents(books):
    for book in books:

        title = book.get("title", "Unknown Title")
        author = book.get("author", "Unknown Author")

        categories = book.get("categories", [])

        if isinstance(categories, list):
            category = ", ".join(categories)
        else:
            category = "Unknown"

        filename = (
            title.replace("/", "-")
                 .replace("\\", "-")
                 .replace(":", "-")
                 .replace("*", "")
                 .replace("?", "")
                 .replace('"', "")
                 .replace("<", "")
                 .replace(">", "")
                 .replace("|", "")
        )

        filepath = os.path.join(DOCUMENTS_FOLDER, f"{filename}.txt")

        with open(filepath, "w", encoding="utf-8") as file:
            file.write(f"Title: {title}\n")
            file.write(f"Author: {author}\n")
            file.write(f"Category: {category}\n")

        print(f"Created: {filename}.txt")


def main():
    books = fetch_books()

    if not books:
        print("No books found.")
        return

    create_documents(books)
    print("\nCorpus created successfully!")


if __name__ == "__main__":
    main()