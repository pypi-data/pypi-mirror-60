from flask import current_app


def _get_casbin():
    try:
        return current_app.extensions['flask-pycasbin']
    except KeyError:  # pragma: no cover
        raise RuntimeError("You must initialize a Pycasbin with this flask "
                           "application before using this method")


def check_permission(request, user):
    if user is None:
        user = 'anonymous'
    path = request.path
    method = request.method
    print(f'check_permission: {user}, {path}, {method}')
    return _get_casbin().enforcer.enforce(user, path, method)
