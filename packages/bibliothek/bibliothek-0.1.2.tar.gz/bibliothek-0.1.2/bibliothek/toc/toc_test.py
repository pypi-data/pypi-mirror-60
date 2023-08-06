from os import mkdir, rmdir

import pytest

from .toc import ToC


@pytest.mark.parametrize(
    ('base', 'file_pattern', 'decorators', 'result'),
    [
        (
            'data', r'^.+\.md',
            [
                lambda x: x.before_generate(lambda: '# Title'),
                lambda x: x.after_generate(lambda: '## LICENSE'),
                lambda x: x.enter_dir(lambda x: f'## {x[-1]}' if len(x) > 0 else None),
                lambda x: x.exit_dir(lambda x: x[-1] if len(x) > 0 else None),
                lambda x: x.on_note(lambda x: f'[{x["Title"]}]({x["Path"]})'),
                lambda x: x.on_sort('*')(lambda x: x['Created Date']),
            ],
            '\n'.join([
                '# Title',
                '[C](data/3.md)',
                '## foo',
                '[B](data/foo/2.md)',
                'foo',
                '## bar',
                '[A](data/foo/bar/1.md)',
                'bar',
                '## LICENSE',
            ]),
        ),
        (
            'data', r'^.+\.md', [], ''
        ),
    ]
)
def test_toc(base, file_pattern, decorators, result):
    t = ToC(base, file_pattern)
    for decorator in decorators:
        decorator(t)
    mkdir('data/baz/')
    assert str(t) == result
    rmdir('data/baz/')
