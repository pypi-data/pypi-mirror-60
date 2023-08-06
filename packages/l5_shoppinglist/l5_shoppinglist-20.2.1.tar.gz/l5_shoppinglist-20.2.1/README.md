# l5_shoppinglist

gtk shoppinglist for librem5

### install and run

install via pip (preferred!)

`python3 -m pip install --user l5_shoppinglist`

and simply run it with:

`python3 -m l5_shoppinglist`

the convenient according desktop shortcut would be at:

`~/.local/share/applications/l5_shoppinglist.desktop`

with the following content:

```
[Desktop Entry]
Categories=Accessories
Comment=Libre shopping list
Exec=python3 -m l5_shoppinglist
Icon=software-installed-symbolic
Name=l5_shoppinglist
NoDisplay=false
Terminal=false
Type=Application
```


### privacy - user data:

as a privacy respecting app l5_shoppinglist makes no network connections.
no data gets collected or sent anywhere - the user is in full control.
the database is a simple json file which could be edited with a text editor.
it is stored at:

`~/.local/l5_shoppinglist/shoppinglist_db.json`


### running the application without pip:

clone the repository e.g. to `~/opt/`

it can be started via `python3 ~/opt/l5_shoppinglist/l5_shoppinglist/__main__.py`

to run it conveniently from the app drawer on librem5,
it is recommended add a `l5_shoppinglist.desktop` file to:

`~/.local/share/applications`

assuming the path of the `__main__.py` file is:

`/home/purism/opt/l5_shoppinglist/l5_shoppinglist/__main__.py`

the .desktop would need the following content:

```
[Desktop Entry]
Categories=Accessories
Comment=Libre shopping list
Exec=python3 /home/purism/opt/l5_shoppinglist/l5_shoppinglist/__main__.py
Icon=software-installed-symbolic
Name=l5_shoppinglist
NoDisplay=false
Terminal=false
Type=Application
```
