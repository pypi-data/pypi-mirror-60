# from .my_cli import cli

# with open('/workspaces/integration-jira-cloud/my-config.yaml', 'r') as configfile:
#   cli(configfile, 'my-gruyere', '/tmp')

from click.testing import CliRunner
from .my_cli import cli

def test_cli():
  runner = CliRunner()
  result = runner.invoke(cli, ['Peter'])
  assert result.exit_code == 0
  assert result.output == 'Hello Peter!\n'