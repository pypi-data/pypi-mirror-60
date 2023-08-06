import datetime

import dictdumper

dumper = dictdumper.PLIST('temp/test.plist')

test_1 = dict(
    foo=-1,
    bar='Hello, world!',
    boo=dict(
        foo_again=True,
        bar_again=memoryview(b'bytes'),
        boo_again=None,
    ),
)
dumper(test_1, name='test_1')

test_2 = dict(
    foo=[1, 2.0, 3],
    bar=(1.0, bytearray(b'a long long bytes'), 3.0),
    boo=dict(
        foo_again=b'bytestring',
        bar_again=datetime.datetime.today(),
        boo_again=float('-inf'),
    ),
)
dumper(test_2, name='test_2')

test_3 = dict(
    foo="string",
    bar=[
        "s1", "s2", "s3",
    ],
    boo=[
        "s4", dict(s="5", j="5"), "s6"
    ],
    far=dict(
        far_foo=["s1", "s2", "s3"],
        far_var="s4",
    ),
    biu="s5",
)
dumper(test_3, name='test_3')
