from django.db.models import TextField, Transform


class KeyTransform(Transform):
    operator = '->'
    nested_operator = '#>'

    def __init__(self, key_name, *args, **kwargs):
        super(KeyTransform, self).__init__(*args, **kwargs)
        self.key_name = key_name

    def as_sql(self, compiler, connection):
        key_transforms = [self.key_name]
        previous = self.lhs
        while isinstance(previous, KeyTransform):
            key_transforms.insert(0, previous.key_name)
            previous = previous.lhs
        lhs, params = compiler.compile(previous)
        if len(key_transforms) > 1:
            #return "(%s %s %%s)" % (lhs, self.nested_operator), [key_transforms] + params
            key_transforms_str = "{%s}" % ",".join(key_transforms)
            return "(%s %s %%s)" % (lhs, self.nested_operator), [key_transforms_str] + params
        try:
            int(self.key_name)
        except ValueError:
            lookup = "'%s'" % self.key_name
        else:
            lookup = "%s" % self.key_name
        return "(%s %s %s)" % (lhs, self.operator, lookup), params        

class KeyTextTransform(KeyTransform):
    operator = '->>'
    nested_operator = '#>>'
    _output_field = TextField()
