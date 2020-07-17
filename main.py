import os
import xml.etree.ElementTree as ET
import re
import sys
import getopt
import shutil

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


def cleanFolder(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


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


def create_file_line2(f, content):
    ff = f.replace('-', '_')
    return f'{ff}:"{content}"'


def create_json_line(f, content):
    ff = f.replace('-', '_')
    return f'"{ff}":"{content}"'


def create_all_file(files, json=False):
    count = len(files)
    newF = "{"
    for index, (key, value) in enumerate(files.items()):
        if (json == True):
            newF += create_json_line(key[:-4], value)
        else:
            newF += create_file_line2(key[:-4], value)
        if index < count - 1:
            newF += ","
        newF += "\n"
    newF += "}"
    return newF


def create_all_file_dict(files):
    count = len(files)
    newF = "["
    for index, (key, value) in enumerate(files.items()):
        newF += '{ key: \"' + key[:-4] + '\", value: \"' + value+'\"}'
        if index < count - 1:
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


def main(argv):
    print("Init")
    here = os.path.abspath(os.path.dirname(__file__))
    inDir = os.path.join(here, basedir)
    outDir = os.path.join(here, 'out')
    isJson = False
    isJs = False
    cleanOutDir = False
    try:
        opts, args = getopt.getopt(
            argv, "jcshi:o:", ["input=", "output=", "js", "json", "clean"])
    except getopt.GetoptError:
        print('main.py - i <inputfile> -o <outputfile> -j -s -c')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(
                'main.py -i <inputfile> -o <outputfile> -j -s \n -i [ --input=] Input folder \n -o [ --output=] Output folder \n -j [ --json] Create json file \n -s [ --js] Create JS file \n -c [ --clean] Clean output folder before conversion')
            sys.exit()
        elif opt in ("-i", "--input"):
            inDir = arg
        elif opt in ("-o", "--output"):
            outDir = arg
        elif opt in ("-j", "--json"):
            isJson = True
        elif opt in ("-s", "--js"):
            isJs = True
        elif opt in ("-c", "--clean"):
            cleanOutDir = True
    print('Input folder: ', inDir)
    print('Output folder: ', outDir)
    files = get_files(inDir)
    allFiles = dict()
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    if files is not None:
        if cleanOutDir:
            print(f'Clean out directory')
            cleanFolder(outDir)
        print(f'Found {len(files)} files')
        for f in files:
            content = adjust_file(os.path.join(inDir, f))
            print(f'Saving file {f}')
            savefile(os.path.join(outDir, f), content)
            allFiles[f] = content
        # Create all icons file
        if isJs:
            print("Create js file")
            savefile(os.path.join(outDir, "all.js"),
                     create_all_file(allFiles))
        if isJson:
            print("Create json file")
            savefile(os.path.join(outDir, "all.json"),
                     create_all_file(allFiles, True))
    else:
        print('No files found')
    print("Finish")


if __name__ == "__main__":
    main(sys.argv[1:])
