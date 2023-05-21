This is simple af script to generate Python data classes from TOML file.

### Usage
To create Python data classes from some TOML file you can just call:
```
python . config.toml config.py
```
This will produce new file (or override existing one) called config.py with gnerated calasses.

If you want to simplify usage of generated classes you can also create factories for them:
```
python . config.toml config.py -f
```
This call will generate a speacial static method `from_dict` for each class.
You can also add `-s / --safe` flag in order to make `from_dict` safier by using get with deafult instead of simple get:
```
python . config.toml config.py -f -s
```
