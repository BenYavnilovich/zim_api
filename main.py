import os
from libzim.reader import Archive
from flask import Flask
import json

def get_zims(zim_path) -> dict:
    """retrives all zim archives from a given directory and returns them as a dict"""
    zims = [x for x in os.listdir(zim_path) if x[-4::1] == ".zim"]
    return {zims[i][0:-4]: Archive(rf"{zim_path}\{zims[i]}") for i in range(len(zims))}

ZIMS = get_zims(r"C:\Users\Ben\OneDrive\Documents\learning\homelab\zim\zimfiles")
app = Flask(__name__)
@app.route('/')
def inex():
    """returns all available zim knowledge base"""
    return json.dumps({"zims" : list(ZIMS.keys())})

@app.route('/<string:zimName>')
def show_zim_main_entry(zimName):
    """returns error or the main entry of the zim"""
    if not zimName in ZIMS:
        return f'zim file "{zimName}" not found, available zims:<br/>{"<br/>".join(ZIMS.keys())}', 404

    return f"{bytes(ZIMS[zimName].main_entry.get_item().content).decode('utf-8')}"

@app.route("/<string:zimName>/index/readable")
def get_index_readable(zimName):
    """returns index of given zim in a semi human readable format"""
    if not zimName in ZIMS:
        return f'zim file "{zimName}" not found, available zims:<br/>{"<br/>".join(ZIMS.keys())}', 404
    zim = ZIMS[zimName]
    output=""
    for i in range(zim.all_entry_count):
        entry = zim._get_entry_by_id(i)
        output += f"{entry.title} : {entry.path} <br>"
    return output

@app.route("/<string:zimName>/index")
def get_index(zimName):
    """returns index of given zim in json"""
    if not zimName in ZIMS:
        return f'zim file "{zimName}" not found, available zims:<br/>{"<br/>".join(ZIMS.keys())}', 404
    zim = ZIMS[zimName]

    json = {"zim":zimName, "articles" : []}
    for i in range(zim.all_entry_count):
        entry = zim._get_entry_by_id(i)
        json["articles"].append({"title": entry.title, "url": entry.path})
    """
    output='{ "articles": ['
    entry = zim._get_entry_by_id(1)
    output += '{"title":' + json.dumps(entry.title) + ' , "url":' + json.dumps(entry.path) + '}'

    for i in range(2,zim.all_entry_count):
        entry = zim._get_entry_by_id(i)
        output += ',{"title":' + json.dumps(entry.title) + ' , "url":' + json.dumps(entry.path) + '}'
    output += "] }"
    """
    return json

@app.route("/<string:zimName>/<path:articlePath>")
def get_article(zimName,articlePath):
    """returns html of requested article (js currently doesn't work)"""
    if not zimName in ZIMS:
        return f'zim file "{zimName}" not found, available zims:\n{"<br/>".join(ZIMS.keys())}'
    print(f"if not ZIMS[{zimName}].has_entry_by_path({articlePath})\n {type(articlePath)}")
    if not ZIMS[zimName].has_entry_by_path(f"{articlePath}"):
        return f'"{zimName}" cant find the article "{articlePath}"'
    return f"{bytes(ZIMS[zimName].get_entry_by_path(articlePath).get_item().content).decode('utf-8')}"

@app.route('/<float:revNo>')
def revision(revNo):
    return 'Revision Number %f' % revNo

if __name__ == '__main__':
    app.run(debug=True)