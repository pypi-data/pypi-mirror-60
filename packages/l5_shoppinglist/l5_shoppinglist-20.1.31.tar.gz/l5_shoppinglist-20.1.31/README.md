# l5_shoppinglist

gtk shoppinglist for librem5

### running the application

it can be started via `python3 l5_shoppinglist/l5_shoppinglist/__main__.py`

but to run it conveniently from the app drawer on librem5,
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
