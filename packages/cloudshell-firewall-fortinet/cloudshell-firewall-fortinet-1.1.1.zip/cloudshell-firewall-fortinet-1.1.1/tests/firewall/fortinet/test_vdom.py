from mock import patch, MagicMock

from cloudshell.firewall.fortinet.runners.configuration_runner import \
    FortiNetConfigurationRunner
from tests.firewall.fortinet.base_test import BaseFortiNetTestCase, CliEmulator, \
    Command, GLOBAL_PROMPT


@patch('cloudshell.cli.session.ssh_session.paramiko', MagicMock())
@patch(
    'cloudshell.cli.session.ssh_session.SSHSession._clear_buffer',
    MagicMock(return_value=''),
)
class TestVdomDevice(BaseFortiNetTestCase):
    def _setUp(self, attrs=None):
        super(TestVdomDevice, self)._setUp(attrs)
        self.runner = FortiNetConfigurationRunner(
            self.logger, self.resource_config, self.api, self.cli_handler)

    def setUp(self):
        self._setUp({
            'Backup Location': '',
            'Backup Type': FortiNetConfigurationRunner.DEFAULT_FILE_SYSTEM,
        })

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_save_config_vdom_device(self, send_mock, recv_mock):
        host = '192.168.122.10'
        ftp_path = 'ftp://{}'.format(host)
        configuration_type = 'running'

        emu = CliEmulator(
            [
                Command(
                    r'^execute backup config ftp FortiNet-{}-\d+-\d+ {}$'.format(
                        configuration_type, host
                    ),
                    'Please wait...\n\n'
                    'Connect to ftp server 192.168.122.10 ...\n\n'
                    'Send config file to ftp server OK.\n\n'
                    '{}'.format(GLOBAL_PROMPT),
                    regexp=True,
                ),
            ],
            is_vdom_device=True,
        )
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.save(ftp_path, configuration_type)

        emu.check_calls()
