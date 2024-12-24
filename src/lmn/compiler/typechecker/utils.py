# file: lmn/compiler/typechecker/utils.py

def unify_types(t1: str, t2: str) -> str:
    """
    Naive numeric priority: i32 < i64 < f64. 
    Adjust for your language.
    """
    # set the priority of each type
    priority = {"i32":1, "i64":2, "f64":3}

    # return the type with higher priority
    return t1 if priority[t1] >= priority[t2] else t2
