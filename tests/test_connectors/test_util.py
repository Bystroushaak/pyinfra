# encoding: utf-8

from __future__ import unicode_literals

from unittest import TestCase

from pyinfra.api.connectors.util import make_unix_command, split_combined_output


class TestConnectorUtil(TestCase):
    def test_split_combined_output_works(self):
        results = split_combined_output([
            ('stdout', 'stdout1'),
            ('stdout', 'stdout2'),
            ('stderr', 'stderr1'),
            ('stdout', 'stdout3'),
        ])

        assert results == (['stdout1', 'stdout2', 'stdout3'], ['stderr1'])

    def test_split_combined_output_raises(self):
        with self.assertRaises(ValueError):
            split_combined_output(['nope', ''])


class TestMakeUnixCommandConnectorUtil(TestCase):
    def test_command(self):
        command = make_unix_command('echo Šablony')
        assert command == "sh -c 'echo Šablony'"

    def test_sudo_command(self):
        command = make_unix_command('uptime', sudo=True)
        assert command == 'sudo -S -H -n sh -c uptime'

    def test_sudo_preserve_env_command(self):
        command = make_unix_command('uptime', sudo=True, preserve_sudo_env=True)
        assert command == 'sudo -S -H -n -E sh -c uptime'

    def test_use_sudo_login_command(self):
        command = make_unix_command('uptime', sudo=True, use_sudo_login=True)
        assert command == 'sudo -S -H -n -i sh -c uptime'

    def test_sudo_user_command(self):
        command = make_unix_command('uptime', sudo=True, sudo_user='pyinfra')
        assert command == 'sudo -S -H -n -u pyinfra sh -c uptime'

    def test_su_command(self):
        command = make_unix_command('uptime', su_user='pyinfra')
        assert command == 'su pyinfra -s `which sh` -c uptime'

    def test_use_su_login_command(self):
        command = make_unix_command('uptime', su_user='pyinfra', use_su_login=True)
        assert command == 'su -l pyinfra -s `which sh` -c uptime'

    def test_command_env(self):
        command = make_unix_command('uptime', env={
            'key': 'value',
            'anotherkey': 'anothervalue',
        })
        assert command in [
            "sh -c 'env key=value anotherkey=anothervalue uptime'",
            "sh -c 'env anotherkey=anothervalue key=value uptime'",
        ]

    def test_custom_shell_command(self):
        command = make_unix_command('uptime', shell_executable='bash')
        assert command == 'bash -c uptime'

    def test_mixed_command(self):
        command = make_unix_command(
            'uptime',
            env={'key': 'value'},
            sudo=True,
            sudo_user='root',
            preserve_sudo_env=True,
            su_user='pyinfra',
            shell_executable='bash',
        )
        assert command == (
            'sudo -S -H -n -E -u root '  # sudo bit
            'su pyinfra -s `which bash` -c '  # su bit
            "'env key=value uptime'"  # command bit
        )
