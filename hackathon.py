# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import json



file_name = 'example.html'


def get_node_text(node):
    """node can be any tag with children, and you want to get inner text out of.
    ex input: <p>text<a>text2</a>text3</p>"""
    
    if node.name == 'p':
        return ' '.join(node.get_text().split('\n'))
    return '\n'.join(node.get_text().split('\n'))   	


def next_p_texts(node):
    """Given a node, it returns a list of the insider texts of all next <p> and <ul>
    tags at same node level. The input node could be a <heading> or a <p> tag.
    """

    if not node or node.name in ['h2', 'h3', 'h4', 'h5', 'h6']:
    	return []
    else:
    	return [get_node_text(node)] + next_p_texts(node.find_next_sibling(['p', 'ul', 'h2', 'h3', 'h4', 'h5', 'h6']))


def next_h_tags(node):
    """Given an <h> node, it returns a list of the adjacent <h> siblings at same node level."""

    if not node or node.name == 'h2':
    	return []
    else:
    	return [node] + next_h_tags(node.find_next_sibling(['h2', 'h3', 'h4', 'h5', 'h6']))


def has_subsection(h2_node):
	"""Returns a tuple (True, first subsection node), if any"""
	
	has_sub = True
	while h2_node and has_sub:
		h2_node = h2_node.next_sibling.next_sibling
		if h2_node and h2_node.name in ['h3', 'h4', 'h5', 'h6']:
			has_sub = True
			break
		if h2_node and h2_node.name == 'h2':
			has_sub = False
	return has_sub, h2_node


def get_subsections(node):
    """Given an <h2> tag, it returns a list of the insider texts of all next <p> and <ul>
    tags at certain hierarchy level."""
    
    subsections = []
    subsection = has_subsection(node)
    if subsection:
        next_sibling = subsection[1]
        for h in next_h_tags(next_sibling):
            subsections.append({
                "subsection": h.get_text(),
                "paragraphs": next_p_texts(h.find_next_sibling(['p', 'ul']))
        })
    return subsections


def extract_headers(parent_node):
    """This method take the parent node with class attribute "body searchable-content", 
    and returns the headers "table of contents" in a JSON format"""

    result = {}

    # in case of getting the first/level-0 <p> tags
    first_node = parent_node.find(['h2', 'p'])
    if first_node and first_node.name == 'p':
        p_tags_initial = next_p_texts(first_node)
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
                "paragraphs": next_p_texts(h2.find_next_sibling(['p', 'ul']))
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
    print ('Please change "example.html" with the correct file name.')
