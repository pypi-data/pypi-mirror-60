import mimetypes


def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or "application/octet-stream"


def encode_multipart_formdata(fields, files):
    """
    Function for encoding multipart/form-data
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = "###"
    L = []
    for (key, value) in fields:
        L.append(f"--{BOUNDARY}")
        L.append(f'Content-Disposition: form-data; name="{key}"')
        L.append("")
        L.append(value)
    for (key, filename, value) in files:
        L.append(f"--{BOUNDARY}")
        L.append(f'Content-Disposition: form-data; name="{key}"; filename="{filename}"')
        L.append(f"Content-Type: {get_content_type(filename)}")
        L.append("")
        L.append(value)
    L.append(f"--{BOUNDARY}--")
    L.append("")

    body = "\r\n".join(L)

    content_type = f"multipart/form-data; boundary={BOUNDARY}"

    return content_type, body.encode()


class TypeChecker:
    def __init__(self):
        self.checkers = {
            "int": self.check_int,
            "float": self.check_float,
            "string": self.check_string,
        }

    def check_int(self, value):
        return isinstance(value, int), value

    def check_float(self, value):
        if isinstance(value, int):
            return True, value
        return isinstance(value, float), value

    def check_string(self, value):
        return isinstance(value, str), value

    def __call__(self, method, **kwargs):
        params = method["params"]
        for k, v in kwargs.items():
            if k == "includes":
                continue
            if (not params) or (k not in params):
                raise ValueError("Unexpected argument: %s=%s" % (k, v))

            t = params[k]
            checker = self.checkers.get(t, None) or self.compile(t)
            ok, converted = checker(v)
            if not ok:
                raise ValueError(
                    "Bad value for parameter %s of type '%s' - %s" % (k, t, v)
                )
            kwargs[k] = converted

    def compile(self, t):
        if t.startswith("enum"):
            f = self.compile_enum(t)
        else:
            f = self.always_ok
        self.checkers[t] = f
        return f

    def compile_enum(self, t):
        terms = [x.strip() for x in t[5:-1].split(",")]

        def check_enum(value):
            return (value in terms), value

        return check_enum

    def always_ok(self, value):
        return True, value
