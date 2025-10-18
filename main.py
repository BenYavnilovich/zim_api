import os
from libzim.reader import Archive
from flask import Flask,redirect
import json
import sys
import argparse


def get_zims(zim_folder_path) -> dict:
    """
    retrives all zim archives from a given directory and returns them as a dict
    """
    zims = [x for x in os.listdir(zim_folder_path) if x[-4::1] == ".zim"]
    return {zims[i][0:-4]: Archive(os.path.join(zim_folder_path,zims[i])) for i in range(len(zims))}

parser = argparse.ArgumentParser()
parser.add_argument('-z', '--zim-path', default="zimfiles", help="path to the direcotry where the zim fiels are located")
parser.add_argument('-e','--external',  action="store_true", help="trigger to expose the app outside of localhost\n"
                                                                  "misght require firewall rule")
args = parser.parse_args()
print(args)

if os.path.isabs(args.zim_path):
    zim_path=args.zim_path
else:
    root_dir = os.path.dirname(os.path.abspath(__file__))
    zim_path=os.path.join(root_dir,args.zim_path)
ZIMS = get_zims(zim_path)

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

@app.route("/<string:zimName>/index/")
def get_index(zimName):
    return redirect(f"/{zimName}/index/0")

@app.route("/<string:zimName>/index/<int:paging_min>")
def get_index_paging(zimName,paging_min):
    """returns index of given zim in json"""
    if not zimName in ZIMS:
        return f'zim file "{zimName}" not found, available zims:<br/>{"<br/>".join(ZIMS.keys())}', 404
    zim = ZIMS[zimName]
    paging_max = paging_min + 1000

    # make sure paiging doesn't exeed number of articles
    if paging_max > zim.all_entry_count: paging_max = zim.all_entry_count

    output = {"zim":zimName, "articles" : []}
    for i in range(paging_min,paging_max):
        entry = zim._get_entry_by_id(i)
        output["articles"].append({"title": entry.title, "url": entry.path, "article_id":i})
        #output["articles"].append({"title": entry.title, "url": f"{URL_STARTER}/{zimName}/{i}", "article_id": i})

    return json.dumps(output)

@app.route("/<string:zimName>/<int:articleID>")
def get_article_by_id(zimName, articleID):
    if not zimName in ZIMS:
        return f'zim file "{zimName}" not found, available zims:\n{"<br/>".join(ZIMS.keys())}',404
    if ZIMS[zimName].all_entry_count <= articleID: return f"this zim hasd only {ZIMS[zimName].all_entry_count} articles", 404
    if articleID < 0: return "haha, verry funny... negative article id", 404
    return f"{bytes(ZIMS[zimName]._get_entry_by_id(articleID).get_item().content).decode('utf-8')}"

@app.route("/<string:zimName>/<path:articlePath>")
def get_article(zimName,articlePath):
    """returns html of requested article (js currently doesn't work)"""
    if not zimName in ZIMS:
        return f'zim file "{zimName}" not found, available zims:\n{"<br/>".join(ZIMS.keys())}', 404
    print(f"if not ZIMS[{zimName}].has_entry_by_path({articlePath})\n {type(articlePath)}")
    if not ZIMS[zimName].has_entry_by_path(f"{articlePath}"):
        return f'"{zimName}" cant find the article "{articlePath}"', 404
    return f"{bytes(ZIMS[zimName].get_entry_by_path(articlePath).get_item().content).decode('utf-8')}"

@app.route('/<float:revNo>')
def revision(revNo):
    return 'Revision Number %f' % revNo

if __name__ == '__main__':
    if args.external:
        app.run(debug=True, host="0.0.0.0")
    else:
        app.run(debug=True)
    #URL_STARTER = "http://0.0.0.0:5000"

