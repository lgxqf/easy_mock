def xxx_setup(req):
    print(req)
    print("xxx_setup")
    req["new"] = "add new property"
    return req


def xxx_teardown(req, resp):
    print(req)
    print(resp)
    print("xxx_teardown")
    return {"resp": resp}
