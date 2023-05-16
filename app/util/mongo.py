from typing import Dict


def make_query(query: Dict):
    res = {}
    for k, v in query.items():
        if isinstance(v, dict):
            mini_query = make_query(v)
            for mk, mv in mini_query.items():
                res[f"{k}.{mk}"] = mv
        else:
            res[k] = v
    return res


def make_body(body: Dict):
    return make_query({"_source": body})
