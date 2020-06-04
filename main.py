import os
import xml.etree.ElementTree as ET
import re

basedir = "icons"
notNeededTags = ['title', 'defs', 'namedview', 'metadata']
notNeededAttrs = ['id', 'style', 'connector',
                  'transform', 'arg1', 'arg2', 'nodetypes']

neededArgs = ['height', 'width', 'x', 'y', 'cx', 'cy', 'r', 'd', 'transform']
removeSpacesRegex = r'((?<=>)(\s+)(?=[<]))'
removeNewlineRegex = r'((?<=>)(\n[\t]*)(?=[^<\t]))|(?<=[^>\t])(\n[\t]*)(?=<)|\n'
childRegex = './'


def get_files(directory):
    if not directory:
        return None
    return os.listdir(directory)


def savefile(f, content):
    with open(f, 'w') as newF:
        newF.write(content)


def getroot(f):
    tree = ET.parse(f)
    return tree.getroot()


def matches(tagName, arr):
    for t in arr:
        if t in tagName:
            return True
    return False


def equals(tagName, arr):
    for t in arr:
        if t == tagName:
            return True
    return False


def regex_replace(text, replaceStr, reg):
    comp = re.compile(reg)
    return re.sub(comp, replaceStr, text)


def prepare_string(text):
    noNewL = regex_replace(text, "", removeNewlineRegex)
    noSpace = regex_replace(noNewL, "", removeSpacesRegex)
    return noSpace.replace("\"", "\\\"")


def get_keys_to_remove(attribs):
    return [key for key in attribs if not(equals(key, neededArgs))]


def create_file_line(f, content):
    return f'"{f}":"{content}"'


def create_all_file(files):
    count = len(files)
    newF = "{"
    for index, (key, value) in enumerate(files.items()):
        newF += create_file_line(key[:-4], value)
        if index < count:
            newF += ","
        newF += "\n"
    newF += "}"
    return newF


def create_all_file_dict(files):
    count = len(files)
    newF = "["
    for index, (key, value) in enumerate(files.items()):
        newF += '{ key: \"' + key[:-4] + '\", value: \"' + value+'\"}'
        if index < count:
            newF += ","
        newF += "\n"
    newF += "]"
    return newF


def adjust_file(f):
    print(f'Parsing file {f}')
    tree = ET.parse(f)
    root = tree.getroot()
    copy = {}
    copy['viewBox'] = root.attrib['viewBox']
    copy['width'] = root.attrib['width']
    copy['height'] = root.attrib['height']
    root.attrib = copy

    for element in root.findall(childRegex):
        if matches(element.tag, notNeededTags):
            root.remove(element)

    # Remove attributes for existing elements
    for element in root.findall(childRegex):
        toRemove = get_keys_to_remove(element.attrib)
        for key in toRemove:
            del element.attrib[key]
    # //print()
    content = ET.tostring(root, encoding='utf8', method='html')
    return prepare_string(content.decode())


def main():
    print("Init")
    here = os.path.abspath(os.path.dirname(__file__))
    pathf = os.path.join(here, basedir)
    outDir = os.path.join(here, 'out')
    files = get_files(pathf)
    allFiles = dict()
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    if files is not None:
        print(f'Found {len(files)} files')
        for f in files:
            content = adjust_file(os.path.join(pathf, f))
            print(f'Saving file {f}')
            savefile(os.path.join(outDir, f), content)
            allFiles[f] = content
        # Create all icons file
        print("Create js file")
        savefile(os.path.join(outDir, "all.js"),
                 create_all_file_dict(allFiles))
    else:
        print('No files found')
    print("Finish")


if __name__ == "__main__":
    main()
