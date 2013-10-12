import urllib2
import re
import pickle
import random

try:
    from BeautifulSoup import BeautifulSoup as soup
except ImportError:
    from bs4 import BeautifulSoup as soup

MINIMUM_WORD_LENGTH = 4
TAGS_TO_REPLACE_WITH_CONTENT = ['font', 'div', 'i', 'p']
TAGS_TO_DELETE = ['script']
SPEAKERS_TO_REMOVE = ['viewscreens', 'transcript']
CONTENT_STRINGS_TO_REPLACE = [
    ("\n", ""),
    (u"\xa0", " "),
    ("  ", " "),
    (" .", "."),
    (" ,", ","),
    (" ?", "?"),
    (": :", ": "),
    ("[ ","["),
    (" ]", "]"),
    (u"\u2013", "-"),
    (" '", "'"),
]
EPISODE_LIST_URL = 'https://sites.google.com/site/qitranscripts/transcripts'


def loop_until(element, until):
    result = []
    while True:
        result.append(getattr(element, 'text', element))

        try:
            if element.nextSibling is None or element.nextSibling == until or hasattr(element.nextSibling, 'name') and until in element.nextSibling:
                break
        except:
            pass

        element = element.nextSibling
    return result


def parse_episode_list():
    """ Get epsiodes list, generate a dictionary of {episode_number: {'description':..., 'url':...}} """
    content = soup(urllib2.urlopen(EPISODE_LIST_URL).read())
    links = content.findAll("a", href = re.compile('.*\/transcripts\/([0-9]+)x([0-9]+).*'))

    episodes = {}
    for link in links:
        episode = {}

        url = link['href']
        episode_number = re.match('.*\/transcripts\/([0-9]+x[0-9]+).*', url).groups()[0]
        episode_info = re.sub(r'\xa0+', u' ', link.text)

        episode['description'] = episode_info or episode_number
        episode['url'] = url
        episode['number'] = episode_number
        episodes[episode_number] = episode

    return episodes


def parse_episode(episode, search_index=None):
    episode_number = episode['number']
    content = soup(urllib2.urlopen(episode['url']).read()).find("body")

    for tag in TAGS_TO_REPLACE_WITH_CONTENT:
        for match in content.findAll(tag):
            match.replaceWithChildren()
    for tag in TAGS_TO_DELETE:
        [s.extract() for s in content('script')]

    def bold_finder(tag):
        if not hasattr(tag, 'name'):
            return False
        try:
            style = tag['style']
        except:
            style = ''
        return tag.name == 'b' or 'font-weight:bold' in style
    headers = content.findAll(bold_finder)
    transcript = []

    line = 0
    for i in range(0, len(headers)-1):
        header = headers[i]
        # Find text starting from the header to the next header
        text_with_header = loop_until(header, headers[i+1])
        text_with_header = [x for x in text_with_header if x.strip() not in ['','\n']]

        # If it's just a header without any text after it, ignore
        if len(text_with_header) < 2:
            continue

        # Get person speaking (text of the header), and the remaining text
        speaker = text_with_header[0]
        for to_replace, replace_with in CONTENT_STRINGS_TO_REPLACE:
            speaker = speaker.replace(to_replace, replace_with)
        speaker = speaker.strip()
        text = text_with_header[1:]

        # Get rid of some things that show up as speaker even though they shouldn't
        if speaker.lower() in SPEAKERS_TO_REMOVE:
            continue

        # Do some processing with the text to get rid of nastiness introduced by the html of the site being a broken mess
        combined = "%s: " % speaker + " ".join(text)
        for to_replace, replace_with in CONTENT_STRINGS_TO_REPLACE:
            combined = combined.replace(to_replace, replace_with)
        combined = combined.strip()
        transcript.append(combined)

        # Put words into the search index. Done at this point so all nastiness is filtered out before
        combined = re.sub(r'[^ a-zA-Z0-9]+', '', combined)
        words = combined.split(" ")
        for word in words:
            if len(word) < MINIMUM_WORD_LENGTH:
                continue

            if search_index:
                word = word.lower()
                if word in search_index:
                    search_index[word].add((episode_number, line))
                else:
                    search_index[word] = set([(episode_number, line)])
        line += 1
    return transcript


def parse_episodes(debug=False, search_index=None):
    episodes = parse_episode_list()

    for episode in sorted(episodes.values()):
        if debug:
            print "Processing episode %s" % episode['description']
        episode['transcript'] = parse_episode(episode, search_index=search_index)

    save(episodes)
    return episodes


def search(episodes, index, string):
    string = string.lower()
    for to_replace, replace_with in CONTENT_STRINGS_TO_REPLACE:
        string = string.replace(to_replace, replace_with)

    if string not in index:
        return []

    locations = sorted(list(index[string]), key=lambda x: "%s_%s" % (x[0], x[1]))
    results = []
    for (episode_number, line) in locations:
        results.append(episodes[episode_number]['transcript'][line])
    return results


def pick(l):
    """ Pick random element from list """
    return random.choice(l)


def save(episodes):#, index):
    episodes_file = open('episodes.bin', 'wb')
    pickle.dump(episodes, episodes_file)
    episodes_file.close()

    #index_file = open('index.bin', 'wb')
    #pickle.dump(index, index_file)
    #index_file.close()


def load():
    try:
        episodes_file = open('episodes.bin', 'rb')
        episodes = pickle.load(episodes_file)
        episodes_file.close()

        #index_file = open('index.bin', 'rb')
        #index = pickle.load(index_file)
        #index_file.close()

        return episodes#, index
    except:
        return parse_episodes(debug=True)#, None


if __name__ == '__main__':
    episodes, index = load()
    if not episodes:
        index = {}
        episodes = parse_episodes(debug=True, search_index=index)
        save(episodes, index)
    import pdb
    pdb.set_trace()
