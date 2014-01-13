# navigator-recorder

navigator-recorder stores Navigator user locations with timestamps.

## Deploy

1. git clone https://github.com/HSLdevcom/navigator-recorder
2. pip install -r requirements.txt
3. Create the database by
```sh
create_db /path/to/trace_database
```
4. Create a new secret key with for example
```python
>>> with open('/dev/random', 'rb') as f:
...     f.read(64)
'u\xc0$\xd3\xa6\xdfH\xef\x1as\t\xfd2\xcc\xfda\x15\x95}\rg/<\x11\xc8^\x95\x16?\x8c\x86I\xe7n\x00\xd3\xefY\x96\xe0\xdfjk\xc2\xed\t\xc94e\xd3>S\\a\x11\x87\xa4cu\xba\xff\xd5\x15\xf9'
```
5. Create a `production_settings.conf` file in the style of `navirec/debug_settings.conf` and change the values to match steps 3 and 4. Set `DEBUG = False` for production deployment. Also protect the secret key and the privacy of your users by controlling access to `production_settings.conf` and the database.
6. Create a script to use your newly-created `production_settings.conf` in the style of `navirec/run_debug`.
7. Run the script.
