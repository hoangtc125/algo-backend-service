from typing import Dict


def make_query(query: Dict):
    res = make_body({"_source": query})
    if "_source._id" in res:
        res["_id"] = res["_source._id"]
        del res["_source._id"]
    return res


def make_body(body: Dict):
    res = {}
    for k, v in body.items():
        if isinstance(v, dict):
            mini_query = make_body(v)
            for mk, mv in mini_query.items():
                res[f"{k}.{mk}"] = mv
        else:
            res[k] = v
    return res
    