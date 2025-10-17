from libzim.writer import Creator, Item, StringProvider, FileProvider, Hint

class MyItem(Item):
    def __init__(self, title, path, content="", fpath=None):
        super().__init__()
        self.path = path
        self.title = title
        self.content = content
        self.fpath = fpath

    def get_path(self):
        return self.path

    def get_title(self):
        return self.title

    def get_mimetype(self):
        return "text/html"

    def get_contentprovider(self):
        if self.fpath is not None:
            return FileProvider(self.fpath)
        return StringProvider(self.content)

    def get_hints(self):
        return {Hint.FRONT_ARTICLE: True}

home = MyItem("Hello Kiwix", "home", "welcom to my first test zim")
secret = MyItem("secret", "secret", "my extremly secret password is 'screwdriver123'")

with Creator("test.zim").config_indexing(True, "eng") as creator:
    creator.set_mainpath("home")
    creator.add_item(home)
    creator.add_item(secret)
    for name, value in {
        "creator": "python-libzim",
        "description": "test zim",
        "name": "my-zim",
        "publisher": "beny",
        "title": "Test ZIM",
        "language": "eng",
        "date": "2025-10-17",
    }.items():
        creator.add_metadata(name.title(), value)
