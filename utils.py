def parse_numstr(string: str):
    return [float(x) for x in string.split(',')]


def create_numstr(floats: list):
    return ','.join([str(round(x, 8)) for x in floats])
