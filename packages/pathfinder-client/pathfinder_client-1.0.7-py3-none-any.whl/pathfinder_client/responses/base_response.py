class BaseResponse(dict):
    def __getattr__(self, item):
        return self[item]
