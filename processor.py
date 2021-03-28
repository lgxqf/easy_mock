def xxx_setup(req):
    print("xxx_setup")
    return req


def xxx_teardown(req, resp):
    print("xxx_teardown")
    return {"resp": resp}
