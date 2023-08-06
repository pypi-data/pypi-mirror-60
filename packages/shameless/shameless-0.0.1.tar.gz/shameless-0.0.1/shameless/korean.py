import csv
import re
from pathlib import Path
from typing import Dict, List

from shameless.shameless import get, pool


def save(dicts: List[Dict], file: str = "temp.csv"):
    lines = [list(d.values()) for d in dicts]
    with open(Path(file), "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerows(lines)


class Scrap:
    @staticmethod
    def ridibooks_fantasy(page: int = 10):
        save(sum(pool(func=Info.ridibooks_fantasy, tasks=list(range(page))), []))

    @staticmethod
    def ridibooks_select(page: int = 10):
        dicts = []
        for i in range(page):
            print(i + 1)
            dicts += Info.ridibooks_select(i)
        save(dicts, "select.csv")


class Info:
    @staticmethod
    def ridibooks_fantasy(page: int) -> List[Dict]:
        soup = get(f"https://ridibooks.com/category/books/1710?order=review_cnt&rent=y&page={page + 1}")
        books = soup.find_all('div', {"class": "book_macro_portrait"})
        author = [b.find("p", {"class": "author"}).text.strip() for b in books]
        genre = [b.find("p", {"class": "genre"}).text.strip() for b in books]
        description = [b.find("p", {"class": "meta_description"}).text.strip() for b in books]
        complete = ["완결" if b.find("span", {"class": "series_complete"}) else "미완" for b in books]
        book = [int(re.match("총 (?P<book>\d+)권", b.find("span", {"class": "count_num"}).text.strip())['book']) if b.find("span", {"class": "count_num"}) else 1 for b in books]
        title = [b.find("span", {"class": "title_text"}).text.strip() for b in books]
        count = [int(b.find("span", {"class": "StarRate_ParticipantCount"}).text.replace("명", "").replace(",", "").strip()) if b.find("span", {"class": "StarRate_ParticipantCount"}) else 0 for b in books]
        score = [float(b.find("span", {"class": "StarRate_Score"}).text.replace("점", "").strip()) if b.find("span", {"class": "StarRate_Score"}) else 0 for b in books]
        keys = ["title", "author", "score", "count", "book", "complete", "genre", "description"]
        infos = list(zip(title, author, score, count, book, complete, genre, description))
        dicts = [dict(zip(keys, info)) for info in infos]
        return dicts

    @staticmethod
    def ridibooks_select(page: int) -> List[Dict]:
        # page: range(32)
        soup = get(f"https://select.ridibooks.com/categories?id={6}&page={page + 1}", chrome=True)
        items = soup.find_all("li", {"class": "GridBookList_Item"})
        books = [int(re.match("/book/(?P<id>\d+)", b.find("a", {"class": "GridBookList_ItemLink"}).attrs['href'])['id']) for b in items]
        # dicts = [Info.ridibooks_detail(book) for book in books]
        dicts = pool(func=Info.ridibooks_detail, tasks=books)
        return dicts

    @staticmethod
    def ridibooks_detail(book: int) -> Dict:
        try:
            soup = get(f"https://ridibooks.com/v2/Detail?id={book}")
            title = soup.find('h3', {'class': 'info_title_wrap'}).text.strip()
            score = float(soup.find("span", {"class": "StarRate_Score"}).text.replace("점", "").strip()) if soup.find("span", {"class": "StarRate_Score"}) else 0
            count = int(soup.find("span", {"class": "StarRate_ParticipantCount"}).text.replace("명", "").replace(",", "").strip()) if soup.find("span", {"class": "StarRate_ParticipantCount"}) else 0
            author = soup.find("a", {'class': 'author_detail_link'}).text.strip()
            description = soup.find("div", {"id": "introduce_book"}).text.replace("펼쳐보기", "").strip()
            keys = ["title", "score", "count", "author", "description"]
            info = (title, score, count, author, description)
            return dict(zip(keys, info))
        except:
            keys = ["title", "score", "count", "author", "description"]
            info = (book, 0, 0, "NA", "NA")
            return dict(zip(keys, info))
