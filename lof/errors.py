class LoFError(Exception):
    pass


class NoTemplate(LoFError):
    def __init__(self, path: str, *args, **kwargs):
        default_msg = f"No template file found on passed path {path}"
        if not args:
            args = (default_msg,)
        super().__init__(*args, **kwargs)


class NoVariablesFile(LoFError):
    def __init__(self, path: str, *args, **kwargs):
        default_msg = f"No variables file found on passed path {path}"
        if not args:
            args = (default_msg,)
        super().__init__(*args, **kwargs)
