from click.testing import CliRunner
from pickaa import cli


def test_picker():
    runner = CliRunner()
    result = runner.invoke(cli, ['1', '2', '3', '4', '5'])
    assert result.exit_code == 0
    assert int(result.output) in [1, 2, 3, 4, 5]
