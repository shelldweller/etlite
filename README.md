# ETlite

Extract/Transform Light - a simple library for reading delimited files.

## Example

Given CSV file:

```
Area id,Male,Female,Area
A12345,34,45,0.25
A12346,108,99,0.32
```

Define a list of transformation:

```python
transformations = [
    # Map existing fields into dictionary.
    # For nested dictionaries use dot.delimited.keys.
    # Optional "via" parameter takes a callable returning transformed value.
    { "from": "Area id", "to": "id" },
    { "from": "Male", "to": "population.male", "via": int },
    { "from": "Female", "to": "population.female", "via": int },
    { "from": "Area", "to": "area", "via": float },

    # You can also add computed values, not present in the original data source.
    # Computer values take transformed dictionary as argument
    # and they do not require "from" parameter:
    {
        "to": "population.total",
        "via": lambda x: x['population']['male'] + x['population']['female']
    },
    # Note that transformations are executed in the order they were defined.
    # This transformation uses population.total value computed in the previous step:
    {
        "to": 'population.density',
        "via": lambda x: round(x['population']['total'] / x['area']),
    }
]
```

Read the file:

```python
from etlite import delim_reader

with open("mydatafile.csv") as csvfile:
  reader = delim_reader(csvfile, transformations)
  data = [row for row in reader]
```

This produces a list of dictionaries:

```python
[
    {
        'id': 'A12345',
        'area': 0.25,
        'population': {
            'male': 34,
            'female': 45,
            'total': 79,
            'density': 316
        }
    },
    {
        'id': 'A12346',
        'area': 0.32,
        'population': {
            'male': 108,
            'female': 99,
            'total': 207,
            'density': 647
        }
    }
]
```

## `delim_reader` options

ETlite is just a thin wrapper on top of Python built-in [CSV module](https://docs.python.org/3/library/csv.html). Thus you can pass to `delim_reader` same options as you would pass to `csv.reader`. For example:

```python
reader = delim_reader(csvfile, transformations, delimiter="\t")
```

## Exception handling

If desired transtormation cannot be performed, ETLite will raise `TransformationError`. If you do not want to abort data loading, you can recover from this error as follows:

```python
from etlite import delim_reader, TransformationError

transformations = [
    # ...
]

with open('my-data.csv') as stream:
    reader = delim_reader(stream, transformations)
    while True:
        try:
            row = next(reader)
        except StopIteration:
            break
        except TransformationError as err:
            print(err)
            print(err.record)
        else:
            do_something(row)
```
