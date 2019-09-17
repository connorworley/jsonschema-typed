from unittest import mock

import pytest
from jsonschema import RefResolver
from mypy.plugin import AnalyzeTypeContext

from jsonschema_typed import plugin


class MockInstance:
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs

    def __eq__(self, other):
        return self.name == other.name \
            and self.args == other.args \
            and self.kwargs == other.kwargs


class MockUnionType:
    def __init__(self, items):
        self.items = items

    def __eq__(self, other):
        return self.items == other.items


@pytest.fixture
def mock_analyze_context():
    with mock.patch.object(plugin, 'UnionType', MockUnionType):
        _mock_analyze_type_context = mock.Mock(spec=AnalyzeTypeContext)
        _mock_analyze_type_context.api.named_type = MockInstance
        yield _mock_analyze_type_context


def test_pattern_properties(mock_analyze_context):
    schema = {
        'type': 'object',
        'patternProperties': {
            '.*': {
                'type': 'integer',
            },
        },
    }
    resolver = RefResolver.from_schema(schema)
    result = plugin.APIv4(resolver, '').get_type(mock_analyze_context, schema, outer=True)

    # We want to end up with a Dict[str, Union[int] type
    assert result == MockInstance(
        'builtins.dict',
        [
            MockInstance(
                'builtins.str',
            ),
            MockUnionType([
                MockInstance(
                    'builtins.int',
                ),
            ]),
        ],
    )


def test_pattern_properties_multiple(mock_analyze_context):
    schema = {
        'type': 'object',
        'patternProperties': {
            'foo': {
                'type': 'boolean',
            },
            '.*': {
                'type': 'integer',
            },
        },
    }
    resolver = RefResolver.from_schema(schema)
    result = plugin.APIv4(resolver, '').get_type(mock_analyze_context, schema, outer=True)

    # We want to end up with a Dict[str, Union[bool, int] type
    assert result == MockInstance(
        'builtins.dict',
        [
            MockInstance(
                'builtins.str',
            ),
            MockUnionType([
                MockInstance(
                    'builtins.bool',
                    [],
                ),
                MockInstance(
                    'builtins.int',
                ),
            ]),
        ],
    )
