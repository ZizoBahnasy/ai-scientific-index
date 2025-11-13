from collections import OrderedDict, defaultdict
from typing import List, Dict

def make_metrics(years_dict: Dict[int, Dict[str, float]]) -> OrderedDict:
    """
    Build an OrderedDict of metrics:
      num_awards_aggregate, amt_awarded_aggregate,
      then for each year descending: num_awards_{Y}, amt_awarded_{Y}
    """
    years = sorted(years_dict.keys(), reverse=True)
    m = OrderedDict()
    m["num_awards_aggregate"]  = sum(v["count"] for v in years_dict.values())
    m["amt_awarded_aggregate"] = sum(v["amt"]   for v in years_dict.values())
    for y in years:
        m[f"num_awards_{y}"] = years_dict[y]["count"]
        m[f"amt_awarded_{y}"] = years_dict[y]["amt"]
    return m

def build_hierarchy(records: List[Dict]) -> Dict[str, Dict]:
    """
    Two-pass aggregation:
      1) bucket by (year → {count, amt}) at program, division, directorate
      2) assemble nested dict with metrics at each level
    """
    prog_buckets = defaultdict(lambda: defaultdict(lambda: {"count":0, "amt":0.0}))
    div_buckets  = defaultdict(lambda: defaultdict(lambda: {"count":0, "amt":0.0}))
    dir_buckets  = defaultdict(lambda: defaultdict(lambda: {"count":0, "amt":0.0}))

    dir_to_divs  = defaultdict(set)
    div_to_progs = defaultdict(set)

    for r in records:
        y, d, v, p, amt = r["year"], r["directorate"], r["division"], r["program"], r["amount"]
        dir_to_divs[d].add(v)
        div_to_progs[(d,v)].add(p)

        prog_buckets[(d,v,p)][y]["count"] += 1
        prog_buckets[(d,v,p)][y]["amt"]   += amt

        div_buckets[(d,v)][y]["count"] += 1
        div_buckets[(d,v)][y]["amt"]   += amt

        dir_buckets[(d,)][y]["count"] += 1
        dir_buckets[(d,)][y]["amt"]   += amt

    hierarchy: Dict[str, Dict] = {}
    for d in dir_to_divs:
        # directorate
        hierarchy[d] = make_metrics(dir_buckets[(d,)])
        for v in dir_to_divs[d]:
            hierarchy[d][v] = make_metrics(div_buckets[(d,v)])
            for p in div_to_progs[(d,v)]:
                hierarchy[d][v][p] = make_metrics(prog_buckets[(d,v,p)])
    return hierarchy

def make_brief(node: Dict) -> Dict:
    """
    Recursively strip out everything except aggregate metrics and children.
    """
    brief = {}
    if "num_awards_aggregate" in node:
        brief["num_awards_aggregate"] = node["num_awards_aggregate"]
    if "amt_awarded_aggregate" in node:
        brief["amt_awarded_aggregate"] = node["amt_awarded_aggregate"]

    for key, val in node.items():
        if isinstance(val, dict) and key not in ("num_awards_aggregate","amt_awarded_aggregate"):
            brief[key] = make_brief(val)
    return brief

def sort_node(node: Dict) -> OrderedDict:
    """
    Sort a single node’s children by their aggregate amount.
    """
    # metrics keys come first
    metrics_keys = [k for k in node.keys()
                    if k.startswith("num_awards_") or k.startswith("amt_awarded_")]
    # all other keys are children
    child_keys = [k for k in node.keys() if k not in metrics_keys]
    # sort children descending by their aggregate
    sorted_children = sorted(
        child_keys,
        key=lambda k: node[k].get("amt_awarded_aggregate", 0),
        reverse=True
    )

    out = OrderedDict()
    for k in metrics_keys:
        out[k] = node[k]
    for k in sorted_children:
        out[k] = sort_node(node[k])
    return out

def sort_hierarchy(tree: Dict[str, Dict]) -> OrderedDict:
    """
    Sort top-level directorates by aggregate, then recurse into each.
    """
    sorted_dirs = sorted(
        tree.keys(),
        key=lambda d: tree[d].get("amt_awarded_aggregate", 0),
        reverse=True
    )
    out = OrderedDict()
    for d in sorted_dirs:
        out[d] = sort_node(tree[d])
    return out

def sort_hierarchy_by_year(tree: Dict[str, Dict], year: int) -> OrderedDict:
    """
    Like sort_hierarchy, but sorts children by amt_awarded_{year} descending.
    """
    def sort_node_year(node: Dict) -> OrderedDict:
        # metrics first (all num_awards_/amt_awarded_ keys)
        metrics_keys = [k for k in node if k.startswith("num_awards_") or k.startswith("amt_awarded_")]
        # children keys
        child_keys = [k for k in node if k not in metrics_keys]
        # sort children by that year's amount, descending
        sorted_children = sorted(
            child_keys,
            key=lambda k: node[k].get(f"amt_awarded_{year}", 0),
            reverse=True
        )
        out = OrderedDict()
        for k in metrics_keys:
            out[k] = node[k]
        for k in sorted_children:
            out[k] = sort_node_year(node[k])
        return out

    # sort top‐level directorates by amt_awarded_{year}
    sorted_dirs = sorted(
        tree,
        key=lambda d: tree[d].get(f"amt_awarded_{year}", 0),
        reverse=True
    )
    out = OrderedDict()
    for d in sorted_dirs:
        out[d] = sort_node_year(tree[d])
    return out