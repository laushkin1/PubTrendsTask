import re
import os
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json
from nltk.stem import PorterStemmer
from collections import Counter
from math import log


PMIDs_list = "PMIDs_list.txt"
DATAFILE = "data.json"
WORDSFILE = "words.txt"


def main():
    create_data_file()
    create_words_file()
    create_result_file()
    remove_temp_file()


def create_data_file() -> None:
    result = {}
    ids_file = get_id_list_from_file(PMIDs_list)
    for id_file in ids_file:
        temp_dict = []
        print("")
        print(f"'{id_file}':")
        id_links = get_id_list_from_link(
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&db=gds&linkname=pubmed_gds&id={id_file}&retmode=xml"
        )
        for id_link in id_links:
            link = get_link_from_id(id_link)
            data = get_data_from_link(get_link_from_id(id_link))
            print(link)
            print(data)
            if link is not None and data is not None:
                temp_dict.append({link: data})

        if len(temp_dict) > 0:
            result[id_file] = temp_dict

    with open(DATAFILE, "w+") as outfile:
        json.dump(result, outfile, indent=2)


def create_words_file() -> None:
    with open(DATAFILE, "r") as outfile:
        data = json.load(outfile)

    words_list = []

    list_of_id = list(data.keys())
    for id in list_of_id:
        for l in range(len(data[id])):
            words = []

            for key, value in list((data[id][l].values()))[0].items():
                [
                    words.append(PorterStemmer().stem(word))
                    for word in re.findall(r"\b[\w’]+\b", value.lower())
                ]

            words_count = len(words)
            count_words = Counter(words)
            count_words = sorted(count_words.items(), key=lambda x: x[1], reverse=True)

            word_frequency_temp_list = []
            for word, frequency in count_words:
                word_frequency_temp_list.append({word: frequency})
                # print(f"{word}: {frequency} -> {tf}")
            print(word_frequency_temp_list)
            print("Words in text: ", words_count)
            words_list.append(word_frequency_temp_list)
            print("")
    print("Count of texts", len(words_list))

    with open(WORDSFILE, "w+") as outfile:
        json.dump(words_list, outfile, indent=2)



def create_result_file() -> None:
    with open(WORDSFILE, "r") as outfile:
        words = json.load(outfile)

    text_count = len(words)

    result = []

    for text in words:
        words_count = 0

        for word_frequency in text:
            for word, frequency in word_frequency.items():
                words_count += frequency

        temp_list = []
        for word_frequency in text:
            for word, frequency in word_frequency.items():
                word_in_text_count = 0
                tf = frequency / words_count

                for text_ in words:
                    for word_frequency_ in text_:
                        for word_, frequency_ in word_frequency_.items():
                            if word_ == word:
                                word_in_text_count += 1

                idf = log(text_count / word_in_text_count)
                temp_list.append({word: tf * idf})

        sorted_temp_list = sorted(temp_list, key=lambda x: list(x.values())[0])
        result.append(sorted_temp_list)

        print(sorted_temp_list)

    with open("result.json", "w+") as outfile:
        json.dump(result, outfile, indent=2)


def get_id_list_from_file(filename: str) -> list:
    id_list = []
    with open(filename) as f:
        for line in f:
            id_list.append(int(line))

    return id_list


def get_id_list_from_link(url: str) -> list:
    response = requests.get(url)
    root = ET.fromstring(response.content)
    id_list = [int(id.text) for id in root.findall(".//LinkSetDb/Link/Id")]
    return id_list


def get_link_from_id(id: int) -> str | None:
    base_url = f"https://www.ncbi.nlm.nih.gov/gds/?term={id}"
    response = requests.get(base_url)
    if response.status_code != 200:
        print("Request Error:", response.status_code)
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "/geo/query/" in href:
            full_link = "https://www.ncbi.nlm.nih.gov" + href
            return full_link

    print("Link not found")
    return None


def get_data_from_link(url: str) -> dict | None:
    response = requests.get(url)
    if response.status_code != 200:
        print("Request Error:", response.status_code)
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    result = {}
    for row in soup.find_all("tr"):
        tds = row.find_all("td")
        if len(tds) >= 2:
            key = tds[0].text.strip().strip()
            value = tds[1].text.strip().strip()
            if key in [
                "Title",
                "Experiment type",
                "Summary",
                "Organism",
                "Overall design",
            ]:
                result[key] = value

    return result



def remove_temp_file() -> None:
    if os.path.exists(DATAFILE):
        os.remove(DATAFILE)
        print(f"File {DATAFILE} deleted")
    else:
        print(f"File {DATAFILE} not found")

    if os.path.exists(WORDSFILE):
        os.remove(WORDSFILE)
        print(f"File {WORDSFILE} deleted")
    else:
        print(f"File {WORDSFILE} not found")


if __name__ == "__main__":
    main()
