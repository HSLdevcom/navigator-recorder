# navigator-recorder

navigator-recorder stores Navigator user locations with timestamps.

## Deploy

1. git clone https://github.com/HSLdevcom/navigator-recorder
2. pip install -r requirements.txt
3. Create the database by
```sh
sqlite3 -init <(cat navirec/sql/*) /path/to/traces.db .quit
```
4. Create a new secret key with for example
```python
>>> import os
>>> os.urandom(24)
'\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
```
5. Create a `production_settings.conf` file in the style of `navirec/debug_settings.conf` and change the values to match the choices in steps 3 and 4. Remember to set `DEBUG = False` for production deployment. Also protect the secret key and the privacy of your users by controlling access to `production_settings.conf` and the database.
6. Create a script to use your newly-created `production_settings.conf` in the style of `navirec/debug_run.sh`.
7. Run the script.
