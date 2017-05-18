import csv
from warnings import warn

def delim_reader(input, transformations, *args, **kwargs):
    rules = []
    for rule in transformations:
        if "to" in rule:
            rules.append(rule)
        else:
            warn("Missing 'to' field in rule %s" % rule)

    reader = csv.DictReader(input, *args, **kwargs)

    for input_row in reader:
        row = {}
        for rule in rules:
            via = rule.get("via", lambda x:x)
            if "from" in rule:
                value = via(input_row[rule["from"]])
            else:
                value = via(row)
            _update_dict(row, rule["to"], value)
        yield row

def _update_dict(dictionary, key, value):
    keys = key.split('.')
    head = keys[0:-1]
    tail = keys[-1]
    for h in head:
        if h not in dictionary:
            dictionary[h] = {}
        dictionary = dictionary[h]
    dictionary[tail] = value
