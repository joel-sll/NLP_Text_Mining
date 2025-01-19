import sys
import os
import time
import requests
import pyarrow
import bs4
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse
import re
import traceback
from typing import TypedDict

class Restaurant(TypedDict):
    source_page: str
    name: str
    claimed: bool
    review_number: int
    overall_rating: float
    ranking: dict[str:int]
    geographic_location: str
    price_range:str
    address: str
    phone_number: str
    opening_hours: list[str]
    detailed_rating: dict[str:int]
    details: dict[str: list[str]]

class Reviews(TypedDict):
    n_contrib: int
    review_score: float
    review_title: str
    review_body: str
    visit_date: dict[str:str]
    visit_context: str
    review_date: dict[str:str]

headers = {
        "User-Agent": "Mozilla/5.0 AppleWebKit/605.1.15 Version/17.4.1 Safari/605.1.15",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,/;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }
    
def restaurant_scraper(urls: list[str], save_path: str, headers: dict[str]):
    if isinstance(urls, str):
        urls = [urls]
        print("to list")
    elif not isinstance(urls, list):  
        print("failed")
        raise Exception("urls should either be a string or a list of string.")
    names = [urls[i].split('-')[4] for i in range(len(urls))]
    for i in range(len(urls)):
        filename = os.path.join(save_path, f"{names[i]}.html")
        os.makedirs(save_path, exist_ok=True)
        while True:
            r = requests.get(urls[i], headers= headers)
            if r.status_code == 200: break
            else: time.sleep(5)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(r.text)
        if i < len(urls): time.sleep(5)
            
def parse_reviews(restaurant: dict[any], headers: dict[str:str], wait_time: int = 10) -> list[Reviews]:
    REVIEWS_PER_PAGE = 15
    SLEEP_TIME = 10

    url = restaurant["source_page"].split("-")
    n_reviews = int(restaurant["review_number"])
    n_review_pages =  n_reviews // 15 + (1 if n_reviews % 15 != 0 else 0)
    reviews = []
    
    for n_page in range(n_review_pages):
        fail = 0
        url.insert(4, f"or{REVIEWS_PER_PAGE * n_page}")
        try:
            fail200 = 0
            r = requests.get("-".join(url), headers=headers)
            while r.status_code != 200:
                fail200 +=1
                print(f"request failed {fail200} times.")
                time.sleep(SLEEP_TIME)
                r = requests.get("-".join(url), headers=headers)
                if fail200 == 10:
                    raise Exception("Failed to recover the reviews 10 times. Please try again later.")
        except Exception as e:
            fail += 1
            traceback.print_exc()
            if fail == 10:
                raise Exception("Could not get the page 10 times. Please try again later")            
        url.pop(4)
        soup_r = BeautifulSoup(r.text).find_all("div", {"data-automation": "reviewCard"})
        print(f"parsing reviews page {n_page+1} out of {n_review_pages}.")
        for current_review in soup_r:
            # Field with visit date and context can be missing
            if len(list(current_review.children)) == 7:
                review_date = dict(zip(["day", "month", "year"],current_review.find_all('div', {"class": "neAPm"}, recursive=False)[-1].text.split()[2:]))
            else:
                review_date = {"day": None, "month": None, "year": None}
            review = {
                "n_contrib": int(current_review.select_one("span.b").text) if current_review.select_one("span.b") is not None else -999,
                "review_score" : float(current_review.select_one('title').text.split()[0].replace(",", ".")),
                "review_title" : current_review.find("div", {"data-test-target": "review-title"}).text,
                "review_body" : current_review.select('div[data-test-target="review-body"] > span > div > div')[0].text,
                "visit_date" : dict(zip(["month", "year"],current_review.select_one('div[data-test-target="review-title"]').findNextSibling().text.split()[:2])),
                "visit_context": current_review.select_one('div[data-test-target="review-title"]').findNextSibling().text.split()[-1],
                "review_date" : review_date
            }
            reviews.append(review)
        time.sleep(SLEEP_TIME)
    return reviews
    
def is_URL(path: str) -> bool:
    try:
        parsed_path = urlparse(path)
        return all([parsed_path.scheme, parsed_path.netloc])
    except:
        return False
        
def get_page(url: str, header: dict[str: str]) -> str:
    fail = 0
    while True:
        try:
            r = requests.get(url, headers= header)
            print(r.status_code)
            if r.status_code == 200:
                return r.text
                break
            fail += 1
            assert fail < 10, f"Failed to grab the page 10 times with error {r.status.code}. Please try again later."
            print(f"Failed to grab the page {fail} times. Error {r.status_code}. Waiting {fail * 5}s before retrying.")
            time.sleep(5 * fail)
        except:
            time.sleep(5)

def get_file(file_path: str) -> str:
    assert os.path.isfile(file_path), f"File {file_path} does not exist or is not a file."
    with open(file_path, "r") as f:
        html = f.read()
    return html
    
def page_parser2(file_path: str, header: dict[str:any], 
        attempt: int = 1, review_parsing: bool = True) -> Restaurant:
    if is_URL(file_path):
        print("downloading page")
        html = get_page(file_path, header)
    else:
        print("recovering file from disk")
        html = get_file(file_path)

    soup = BeautifulSoup(html)

    template1_done = False
    template2_done = False

    restaurant_dict = {}
    restaurant_dict["source_page"] = soup.find("link", {"rel": "canonical"})["href"]
    restaurant_dict["details"] = {}
    restaurant_detail_info = soup.find("div", {"data-test-target": "restaurant-detail-info"})
    restaurant_dict["name"] = restaurant_detail_info.select_one("div > h1, div > span > h1").text
    restaurant_dict["claimed"] = 1 if soup.find("path", {"d": "m11.994 2.195 2.52 2.065 3.252-.19.82 3.15 2.742 1.743-1.188 3.042 1.188 3.03-2.742 1.754-.82 3.14-3.252-.188-2.52 2.065-2.509-2.065-3.25.189-.821-3.141-2.742-1.754 1.188-3.03-1.188-3.042 2.742-1.742.82-3.15 3.251.189zm.002 1.94L9.985 5.792l-2.61-.151-.659 2.53-2.198 1.397.952 2.439-.952 2.43 2.198 1.406.66 2.519 2.609-.151 2.011 1.655 2.02-1.655 2.609.15.659-2.518 2.198-1.407-.952-2.43.952-2.438-2.198-1.397-.66-2.53-2.608.151zm4 6.33-5.02 5.02-2.99-2.978 1.058-1.063 1.93 1.922 3.96-3.961z"}) else 0

    restaurant_dict["rating"] = restaurant_detail_info.select_one("div:nth-of-type(2) svg > title").text.split(" ")[0]
    restaurant_dict["review_number"] = restaurant_detail_info.select_one("div:nth-of-type(2) svg title").parent.find_next_sibling().text.split(" ")[0]

    restaurant_dict["review_number"] = re.sub("\u202f", '', restaurant_dict["review_number"])

    rank_info =  re.findall(r"\d+", restaurant_detail_info.select_one("div:nth-of-type(2) > span:nth-of-type(2)").text)
    restaurant_dict["ranking"] = {"rank": rank_info[0], "over": rank_info[1]}

    # print(len(list(restaurant_detail_info.children)))
    if len(list(restaurant_detail_info.children)) == 2: # template #1
        restaurant_dict["price_range"] = restaurant_detail_info.select_one("div:nth-of-type(2) > span:nth-of-type(3) > span:last-of-type").text
        restaurant_dict = parse_template1(soup, restaurant_dict)
        template1_done = True

    else: #template 2
        restaurant_dict["price_range"] = restaurant_detail_info.select_one("div:nth-child(2) > span:nth-of-type(3) > span:nth-child(1)").text
        restaurant_dict = parse_template2(soup, restaurant_dict)
        template2_done = True

    # Pictures
    carousel_tag = soup.find("div", {"data-section-signature": "photo_viewer"})
    pictures_links = set(link.split("?")[0] for link in [tag["srcset"].split(" ")[0] for tag in carousel_tag.select("source")])
    restaurant_dict["photos"] = pictures_links
    
    restaurant_dict["address"] = soup.select_one("div[data-automation=restaurantsMapLinkOnName], span[data-automation=restaurantsMapLinkOnName]").text
    if soup.find("path", {"d": "m6.405 2.13 5.173 5.177-1.826 2.725.096.207c.166.348.427.828.8 1.347.707.986 1.796 2.082 3.383 2.7l3.167-1.355 4.672 4.675-3.153 4.2-.32.037-.086-.745.086.745h-.004l-.006.001-.018.002-.06.005q-.074.007-.205.012c-.175.008-.424.01-.737-.004a12.5 12.5 0 0 1-2.557-.398c-2.11-.547-4.89-1.795-7.668-4.575-2.782-2.783-4.037-5.574-4.591-7.69a12.7 12.7 0 0 1-.41-2.568 9 9 0 0 1 .004-.946l.005-.06.002-.017v-.009s.001-.002.747.08l-.746-.082.036-.325zM3.63 6.067q-.003.191.01.488c.027.537.115 1.318.362 2.262.493 1.883 1.624 4.432 4.2 7.01 2.573 2.574 5.111 3.697 6.984 4.183.94.243 1.715.328 2.25.352q.294.012.485.007l1.969-2.622-3.035-3.037-2.773 1.186-.273-.094c-2.115-.726-3.516-2.137-4.38-3.34a10.5 10.5 0 0 1-.934-1.574 8 8 0 0 1-.29-.682l-.004-.013-.002-.004v-.002s-.001-.001.71-.242l-.711.24-.119-.35 1.567-2.339L6.26 4.108z"}):
        restaurant_dict["phone_number"] = soup.find("path", {"d": "m6.405 2.13 5.173 5.177-1.826 2.725.096.207c.166.348.427.828.8 1.347.707.986 1.796 2.082 3.383 2.7l3.167-1.355 4.672 4.675-3.153 4.2-.32.037-.086-.745.086.745h-.004l-.006.001-.018.002-.06.005q-.074.007-.205.012c-.175.008-.424.01-.737-.004a12.5 12.5 0 0 1-2.557-.398c-2.11-.547-4.89-1.795-7.668-4.575-2.782-2.783-4.037-5.574-4.591-7.69a12.7 12.7 0 0 1-.41-2.568 9 9 0 0 1 .004-.946l.005-.06.002-.017v-.009s.001-.002.747.08l-.746-.082.036-.325zM3.63 6.067q-.003.191.01.488c.027.537.115 1.318.362 2.262.493 1.883 1.624 4.432 4.2 7.01 2.573 2.574 5.111 3.697 6.984 4.183.94.243 1.715.328 2.25.352q.294.012.485.007l1.969-2.622-3.035-3.037-2.773 1.186-.273-.094c-2.115-.726-3.516-2.137-4.38-3.34a10.5 10.5 0 0 1-.934-1.574 8 8 0 0 1-.29-.682l-.004-.013-.002-.004v-.002s-.001-.001.71-.242l-.711.24-.119-.35 1.567-2.339L6.26 4.108z"}).parent.parent.find_next_sibling().text
    else:
        restaurant_dict["phone_number"] = "Non renseigné"
    reviews_tag = soup.select_one("section[id=REVIEWS] div[aria-label='Filtrer les avis']").text
    pattern = r"([A-Za-zéè ]+)(\d+)"

    restaurant_dict["detailed_rating"] = {key: val for key, val in re.findall(pattern, reviews_tag)}
    
    if is_URL(file_path) and review_parsing:
        reviews = parse_reviews(restaurant=restaurant_dict, headers=header)
        restaurant_dict["reviews"] = reviews
        if template1_done and not template2_done:
            while (len(list(restaurant_detail_info.children)) != 3) and (attempt < 1):
                print(f"Attempt #{attempt + 1} to get template 2")
                html2 = get_page(file_path, header)
                soup = BeautifulSoup(html2)
                attempt += 1
                time.sleep(5)
            restaurant_dict = parse_template1(soup, restaurant_dict)
        else:
            while (len(list(restaurant_detail_info.children)) != 2) and (attempt < 1):
                print(f"Attempt #{attempt + 1} to get template 1")
                html2 = get_page(file_path, header)
                soup = BeautifulSoup(html2)
                attempt += 1
                time.sleep(5)
            restaurant_dict = parse_template2(soup, restaurant_dict)
    return restaurant_dict

    
    
def parse_template1(soup: bs4.BeautifulSoup, restaurant: Restaurant) -> Restaurant:
    print(f"template1 {restaurant['name']}")
    overview_tab = soup.find_all("div", {"data-automation": "OVERVIEW_TAB_ELEMENT"})
    # template1 should only have 1 OVERVIEW_TAB_ELEMENT. If more are detected we found a new template or template1 was modified.
    if len(overview_tab) != 1:
        # return overview_tab
        print(len(overview_tab))
        print("More than 1 OVERVIEW_TAB_ELEMENT found. Saving html to file before exiting the program.")
        with open("new_template.html", "w") as f:
            f.write(soup.prettify())
        sys.exit()

    restaurant_info_tag = list(overview_tab[0].find("div", {"class":'NbOQL e'}).children)
    if len(restaurant_info_tag) == 4:
        # print(4)
        restaurant["details"]["traveler's choice"] = restaurant_info_tag[0].select_one("div > div:nth-child(1)").text
        restaurant["details"]["info"] = restaurant_info_tag[1].select_one("div > div:nth-child(1) > div:nth-child(1)").text
    else:
        # print(3)
        restaurant["details"]["Info"] = restaurant_info_tag[0].select_one("div:nth-child(1) > div:nth-child(1) > div:nth-child(1)").text
    fonctionnalites_tag =  [tag.text for tag in overview_tab[0].select("div > div.NbOQL.e > div.vtgrn.u.A.QA > div.BhTGV.e > div > div[class='kYFok f e Q1'] > div.biGQs._P.UFJyF.Wf")]
    fonctionnalites_values = [tag.find_next_sibling().text for tag in overview_tab[0].select("div > div.NbOQL.e > div.vtgrn.u.A.QA > div.BhTGV.e > div > div[class='kYFok f e Q1'] > div.biGQs._P.UFJyF.Wf")]
    fonctionnalites_dict = {key : val for key, val in zip(fonctionnalites_tag, fonctionnalites_values)}
    fonctionnalites_dict["Fonctionnalités"] = [tag.text for tag in overview_tab[0].select("div.Q2")]
    restaurant["details"]["fonctionnalités"] = fonctionnalites_dict
    try:
        opening_hours_text = [tag.text for tag in soup.find_all("div", {"class": "f e Q3"})][1]

        pattern = r'([A-Za-zé]+)((\d{1,2}:\d{2}-\d{1,2}:\d{2}){1,2}|Fermé)'
        opening_hours = {day: (h1, h2)  for day, h1, h2 in re.findall(pattern, opening_hours_text)}
    except:
        opening_hours = "Non disponible"
    restaurant["opening_hours"] = opening_hours

    return restaurant

def parse_template2(soup: bs4.BeautifulSoup, restaurant: Restaurant)-> Restaurant:
    print(f"template2 {restaurant['name']}")
    overview_tab = soup.find_all("div", {"data-automation": "OVERVIEW_TAB_ELEMENT"})
    # template2 should have 3 OVERVIEW_TAB_ELEMENT. If anything else is detected we found a new template or template2 was modified.
    if len(overview_tab) != 3:
        print("Incorrect number of OVERVIEW_TAB_ELEMENT found. Saving html to file before exiting the program.")
        with open("new_template.html", "w") as f:
            f.write(soup.prettify())
        sys.exit()
    ratings_tag = [tag.text for tag in overview_tab[0].select("span[class='biGQs _P pZUbB biKBZ hmDzD']")]
    ratings_value = [tag.text.split(' ')[0] for tag in overview_tab[0].select("div[class='YwaWb u f'] title")]
    restaurant["details"]["ratings"] = {tag: rating for tag, rating in zip(ratings_tag, ratings_value)}

    return restaurant
    
def flatten_restaurant(restaurant: Restaurant)-> dict[any]:
    flattened_restaurant = {key: restaurant[key] for key in restaurant.keys() if key not in  ["details", "opening_hours", "photos"]}
    for key in restaurant["details"]:
        flattened_restaurant[key] = restaurant["details"][key]
    if restaurant.get('opening_hours') and isinstance(restaurant.get('opening_hours'), dict):
        flattened_restaurant["opening_hours"] = {day: ', '.join(times) for day, times in restaurant['opening_hours'].items()}
    else:
        flattened_restaurant["opening_hours"] = "Non disponible"
    flattened_restaurant["photos"] = list(restaurant['photos'])
    return flattened_restaurant
    