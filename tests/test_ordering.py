# pylint: disable=redefined-outer-name,expression-not-assigned,attribute-defined-outside-init,no-member

from expecter import expect

import yorm

from . import strip


@yorm.attr(status=yorm.types.Boolean)
@yorm.attr(label=yorm.types.String)
class StatusDictionary(yorm.types.Dictionary):
    """Sample dictionary converter with ordered attributes."""


@yorm.attr(string=yorm.types.String)
@yorm.attr(number_int=yorm.types.Integer)
@yorm.attr(dictionary=StatusDictionary)
@yorm.attr(number_real=yorm.types.Float)
@yorm.attr(truthy=yorm.types.Boolean)
@yorm.attr(falsey=yorm.types.Boolean)
@yorm.sync("sample.yml")
class Sample:
    """Sample class with ordered attributes."""


def test_attribute_order_is_maintained(tmpdir):
    tmpdir.chdir()
    sample = Sample()
    sample.string = "Hello, world!"
    sample.number_int = 42
    sample.number_real = 4.2
    sample.truthy = False
    sample.falsey = True
    sample.dictionary['status'] = 1

    expect(sample.__mapper__.text) == strip("""
    string: Hello, world!
    number_int: 42
    dictionary:
      status: true
      label: ''
    number_real: 4.2
    truthy: false
    falsey: true
    """)


def test_existing_files_are_reorderd(tmpdir):
    tmpdir.chdir()
    with open("sample.yml", 'w') as stream:
        stream.write(strip("""
        falsey: 1
        number_int: 2
        number_real: 3
        string: 4
        truthy: 5
        dictionary: {label: foo}
        """))
    sample = Sample()
    sample.falsey = 0

    expect(sample.__mapper__.text) == strip("""
    string: 4
    number_int: 2
    dictionary:
      status: false
      label: foo
    number_real: 3.0
    truthy: true
    falsey: false
    """)
