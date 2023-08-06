import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from dataclasses import dataclass, field, fields
from typing import List
import shutil
from pathlib import Path
from tinydb import TinyDB, Query

# TODO delete items
# TODO delete shops
# TODO deb packaging


@dataclass
class Article:
    done:   bool = field(default=False,
                         metadata={"active": 0,
                                   'cell_renderer': Gtk.CellRendererToggle()})
    name:   str  = field(default="",
                         metadata={"text": 1,
                                   'cell_renderer': Gtk.CellRendererText()})
    amount: int  = field(default=1 ,
                         metadata={"text": 2,
                                   'cell_renderer': Gtk.CellRendererText()})
    unit:   str  = field(default="",
                         metadata={"text": 3,
                                   'cell_renderer': Gtk.CellRendererText()})

    def __post_init__(self):
        if not self.amount:
            self.amount = 1
        elif str(self.amount).isnumeric():
            self.amount = int(float(self.amount))
        else:
            self.amount = 1

@dataclass
class ShoppingList:
    name:     str  = ""
    articles: list = List[Article]


class MainWindow(Gtk.Window):

    def __init__(self, shops):
        Gtk.Window.__init__(self, title="shopping_list", border_width=2)
        self.set_default_size(360, 720)

        self.layout  = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.layout)

        self.data_types = list(Article.__annotations__.values())

        self.trees  = {}
        self.shops  = {}
        self.shop_selector = Gtk.ComboBoxText()
        for shop in shops:
            self.shop_selector.append_text(shop.name)
            self.trees[shop.name] = self.build_tree(shop)
            self.shops[shop.name] = shop

        self.shop_selector.set_active(0)
        self.shop_selector.connect("changed", self.swap_list)

        self.adders = Gtk.Box()
        self.add_shop_btn = Gtk.Button(label="add_shop")
        self.add_shop_btn.connect("clicked", self.add_shop)
        self.adders.pack_start(self.add_shop_btn, True, True, 0)
        self.add_item_btn = Gtk.Button(label="add_item")
        self.add_item_btn.connect("clicked", self.add_item)
        self.adders.pack_end(self.add_item_btn, True, True, 0)
        self.layout.add(self.adders)

        self.layout.add(self.shop_selector)
        self.current_tree = self.trees[self.shop_selector.get_active_text()]
        self.current_shop = self.shops[self.shop_selector.get_active_text()]
        self.scrolled_layout = Gtk.ScrolledWindow()
        self.scrolled_layout.set_vexpand(True)
        self.layout.pack_start(self.scrolled_layout, True, True, 0)
        self.scrolled_layout.add(self.current_tree)

    def build_tree(self, shop):
        articles = shop.articles
        store = Gtk.ListStore(*self.data_types)

        for article in articles:
            article_data = list(article.__dict__.values())
            store.append(article_data)
        tree = Gtk.TreeView(model=store, name=shop.name)

        for i, d_field in enumerate(fields(Article)):
            column_info = {"title": d_field.name}
            column_info.update(d_field.metadata)
            column = Gtk.TreeViewColumn(**column_info)
            column.set_sort_column_id(i)
            tree.append_column(column)

        selected_row = tree.get_selection()
        selected_row.connect("changed", self.toggle_done)
        return tree

    def toggle_done(self, selection):
        if not selection.get_selected_rows()[1]: # skip on deselection
            return
        model, treeiter = selection.get_selected()
        print(f"clicked treeiter: {[e for e in model[treeiter]]}")
        model[treeiter][0] = not model[treeiter][0]
        item_name = model[treeiter][1]
        item_done = model[treeiter][0]
        selection.unselect_all()

        update = {"done": item_done}
        print(update)
        current_shop_name = self.current_tree.get_name()
        query = Query().name
        DB.table(current_shop_name).upsert(update, query == item_name)

    def swap_list(self, widget):
        target = widget.get_active_text().strip()
        print(f"swap to: {target}")
        self.scrolled_layout.remove(self.current_tree)
        self.current_tree = self.trees[target]
        self.current_shop = self.shops[target]
        self.scrolled_layout.add(self.current_tree)
        self.scrolled_layout.show_all()

    def add_item(self, widget):

        data_from_user = self.get_data_from_user({
            "dialog_title": "article data",
            "topics": ["name", "amount", "unit"],
        })

        if not data_from_user:
            return

        if not data_from_user["name"]:
            print("got no data")
            return

        current_shop_name = self.current_tree.get_name()
        print(current_shop_name)
        print("added item from", widget)

        new_item = Article(**data_from_user)
        print(new_item)
        article_data = list(new_item.__dict__.values())
        tree_model = self.current_tree.get_model()
        print(tree_model)
        tree_model.append(article_data)
        self.current_shop.articles.append(new_item)
        print(self.current_shop.articles)

        query = Query().name
        DB.table(current_shop_name).upsert(data_from_user, query == data_from_user["name"])

    def add_shop(self, widget):

        data_from_user = self.get_data_from_user({
            "dialog_title": "shop name",
            "topics":       ["name"],
        })

        if not data_from_user:
            return

        if not data_from_user["name"]:
            print("got no data")
            return

        new_shop_name = data_from_user["name"]
        if new_shop_name in self.shops:
            print("we have that shop already")
            return

        print("added shop from", widget)
        new_shop = ShoppingList(name=new_shop_name, articles=[])
        self.shop_selector.append_text(f"\n{new_shop.name}\n")
        self.trees[new_shop.name] = self.build_tree(new_shop)
        self.shops[new_shop.name] = new_shop

        DB.table(new_shop_name)

    def get_data_from_user(self, data_request):
        dialog = DataInput(self, **data_request)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("clicked ok")
            data_from_user = {}
            for row in dialog.store:
                data_from_user[row[0]] = row[1]
                print(row[0], row[1])

            dialog.destroy()
            return data_from_user
        elif response == Gtk.ResponseType.CANCEL:
            print("clicked cancel")
            dialog.destroy()
            return


class DataInput(Gtk.Dialog):

    def __init__(self, parent, dialog_title, topics):
        Gtk.Dialog.__init__(self, f"please enter {dialog_title}",
                            parent, Gtk.DialogFlags.MODAL,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))
        self.set_default_size(360, 180)
        self.set_border_width(10)

        area = self.get_content_area()

        self.store = Gtk.ListStore(str, str)
        for topic in topics:
            self.store.append([topic, ""])

        tree = Gtk.TreeView(model=self.store, name="input_tree")
        column_titles = ["desc", "data"]

        for i, title in enumerate(column_titles):
            renderer = Gtk.CellRendererText()
            if title == "data":
                renderer.set_property("editable", True)
                renderer.connect("edited", self.on_data_edited)
            column = Gtk.TreeViewColumn(
                title=title,
                cell_renderer=renderer,
                text=i
            )
            column.set_sort_column_id(i)
            tree.set_enable_search(False)
            tree.get_selection()
            tree.append_column(column)
        tree.set_enable_search(False)
        tree.set_headers_visible(False)
        area.add(tree)

        self.show_all()

    def on_data_edited(self, widget, path, text):
        print(widget, path, text)
        self.store[path][1] = text


SCRIPT_DIR = Path(__file__).parent
INIT_DB_PATH = SCRIPT_DIR / "db" / "shoppinglist_template_db.json"

USER_DIR = Path.home().absolute()
USER_DB_DIR = USER_DIR / ".config" / "l5_shoppinglist"
USER_DB_DIR.mkdir(exist_ok=True, parents=True)
DB_PATH = USER_DB_DIR / "shoppinglist_db.json"

if not DB_PATH.exists():
    shutil.copy(INIT_DB_PATH, DB_PATH)

JSON_FORMAT = {"sort_keys": True, "indent": 4, "separators": (',', ': ')}
TinyDB.DEFAULT_TABLE = 'config'
DB = TinyDB(DB_PATH, **JSON_FORMAT)

shops = []
shop_map = {}
for table_name in DB.tables():
    if table_name == TinyDB.DEFAULT_TABLE:
        continue
    shop_map[table_name] = DB.table(table_name)
    shop_articles = []
    for article in shop_map[table_name].all():
        shop_articles.append(Article(**article))
    shops.append(ShoppingList(table_name, shop_articles))


css = b"""
button.text-button {padding: 20px}
button.combo {padding: 20px}
window.box.box.button.label {color: blue; background-color: red}
treeview.view header button {padding-left: 8px; padding-top: 15px; padding-bottom: 15px}
treeview {padding-left: 4px; padding-top:10px; padding-bottom:10px}
menuitem {padding: 20px}
"""

style_provider = Gtk.CssProvider()
style_provider.load_from_data(css)
Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(),
    style_provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)

window = MainWindow(shops)
window.connect("delete-event", Gtk.main_quit)
window.show_all()
Gtk.main()
