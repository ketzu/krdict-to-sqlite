# Korean Learners Dictionary Database From JSON

The [korean learners dictionary](https://krdict.korean.go.kr/openApi/openApiInfo) is shared as a json or xml download under CC-BY-SA.

These are my scripts to turn the json export into a sqlite database.

## Usage

Extract the json files into a `data/` subdirectory.

### Simplify JSON

`uv run simplify.py`

To simplify the json. (This is a useful intermediate step even if you want to work with the json.)
This will turn all instances of "att": "a", "val": "b" into a single key value pair "a": "b", fold "feat" blocks into parents and some small things more.

It does *not* unify array | dict types where a key might sometimes have dicts or strings as values and other times an array. 

### Turn simplified JSON into DB

`uv run db.py`

Will create a sqlite database called `lexicon.db` with a schema defined in `db.py`.