class PathfinderException(Exception):
    pass


class PathfinderAuthorizationError(PathfinderException):
    pass


class PathfinderUnauthorized(PathfinderAuthorizationError):
    pass


class PathfinderForbidden(PathfinderAuthorizationError):
    pass


class PathfinderBadRequest(PathfinderException):
    pass
