#!/usr/bin/python3
# coding: utf8

import bs4
import os
import re
import unidecode
import collections
import nltk


def slugify(text):
    text = unidecode.unidecode(text).lower()
    return re.sub(r'\W+', '-', text).strip(" -")


def normalize(html):
    soup = bs4.BeautifulSoup(html, 'lxml')

    for ul in soup.find_all('ul'):
        ul.decompose()

    sentences = []

    for p in soup.find_all('p'):
        for sent in nltk.sent_tokenize(p.text.strip()):
            if not sent.endswith('.'):
                continue

            if sent.startswith('NIH'):
                continue

            if sent.startswith('Instituto'):
                continue

            if sent.startswith('Agencia'):
                continue

            if sent.startswith('Oficina'):
                continue

            if len(sent.split()) <= 4:
                continue

            sentences.append(sent)

    return sentences


def main():
    summaries = collections.defaultdict(lambda: [])

    for filename in os.listdir("data"):
        print(filename, end=' ', flush=True)

        with open(os.path.join("data", filename)) as fp:
            print("(reading)", end=' ', flush=True)
            data = fp.read()
            print("(parsing)", end=' ', flush=True)
            tree = bs4.BeautifulSoup(data, 'lxml')

            print("(processing)", end=' ', flush=True)
            for topic in tree.find_all('health-topic'):
                title = topic.attrs['title']
                language = topic.attrs['language']

                if language == "Spanish":
                    summary = topic.find('full-summary').text
                    group = topic.find('group').text

                    summaries[group].append(dict(
                        summary=summary,
                        source=filename,
                        title=title
                    ))

            print("[done]", end='\n', flush=True)

    total = 0

    for group, items in summaries.items():
        title = slugify(group)
        print(title)

        with open("../data/TASS-2018/corpus/%s.txt" % title, "w", encoding="utf8") as fp:
            open("../data/TASS-2018/corpus/%s.ann" % title, "w").close()

            for summary in items:
                for sent in normalize(summary['summary']):
                    fp.write('%s\n' % sent)
                    total += 1

    print("Total: %i sentences in %i documents" % (total, len(summaries)))

if __name__ == '__main__':
    main()
