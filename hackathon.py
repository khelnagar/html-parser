# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import json

file_name = 'inputs/5bd6c00d652cfa3480dff05398d0e4b6'


def get_node_text(node):
    """node can be any tag with children, and you want to get inner text out of.
    ex input: <p>text<a>text2</a>text3</p>"""

    return ' '.join(node.get_text().split('\n'))


def next_p_texts(node, include_first=False):
    """Given a node, it returns a list of the insider texts of all next <p> and <ul>
    tags at same node level. The input node could be a <heading> or a <p> tag.
    """

    p_tags_texts = []

    # in case of getting the first/level-0 <p> tags, we include the input node itself
    if include_first:
        p_tags_texts = [node.get_text()]

    # next_siblings is a generator object yielding one element/sibling at a time
    for sib in node.next_siblings:
        if sib.name == 'ul':
            p_tags_texts.append(sib.get_text())
        elif sib.name == 'p':
            p_tags_texts.append(get_node_text(sib))
        if sib.name in ['h2', 'h3', 'h4', 'h5', 'h6']:
            break
        else:
            continue

    return p_tags_texts


def next_h_tags(node):
    """Given an <h> node, it returns a list of the adjacent <h> siblings at same node level."""

    h_tags = []

    for sib in node.next_siblings:
        if sib.name in ['h3', 'h4', 'h5', 'h6']:
            h_tags.append(sib)
        elif sib.name == 'h2':
            break
        else:
            continue

    return h_tags


def get_subsections(node):
    """Given an <h2> tag, it returns a list of the insider texts of all next <p> and <ul>
    tags at certain hierarchy level."""
    subsections = []
    for h in next_h_tags(node):
        subsections.append({
            "subsection": h.get_text(),
            "paragraphs": next_p_texts(h)
        })
    return subsections


def extract_headers(parent_node):
    """This method take the parent node with class attribute "body searchable-content", 
    and returns the headers "table of contents" in a JSON format"""

    result = {}

    first_node = parent_node.find(['h2', 'p'])
    if first_node and first_node.name == 'p':
        p_tags_initial = next_p_texts(first_node, include_first=True)
        result.update({
            "paragraphs": p_tags_initial
        })

    h2_tags = parent_node.find_all('h2')
    if h2_tags:
        result.update({
            "sections": []
        })

        for h2 in h2_tags:
            section = {
                "section": h2.get_text(),
                "paragraphs": next_p_texts(h2)
            }

            subsections = get_subsections(h2)
            if subsections:
                section.update({
                    "subsections": subsections
                })

            result['sections'].append(section)

    return result


try:
    with open(file_name, encoding='utf-8') as f:
        contents = f.read()
    soup = BeautifulSoup(contents, 'html.parser')
    parent_node = soup.find('div', class_="body searchable-content")

    with open(file_name + '.result.json', 'w', encoding='utf8') as outfile:
        json.dump(extract_headers(parent_node), outfile, ensure_ascii=False)

except IOError as e:
    print ('Please change "example.html" with your correct file name.')
