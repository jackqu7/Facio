"""
.. module:: tests.test_config
   :synopsis: Tests for the facio config module.
"""

import sys

from docopt import DocoptExit
from facio import config
from facio.config import Config
from mock import PropertyMock, patch

from . import BaseTestCase


class ConfigTests(BaseTestCase):
    """ Argument Passing & Config Tests. """

    base_args = ['test_skeleton', ]

    def setUp(self):
        """ Config Test Setup
        Mocking stdout / stdin / stderr """

        self.clint_paths = [
            'facio.config.puts',
        ]
        self._mock_clint_start()
        sys.argv = ['facio', ]
        self._old_sys_argv = sys.argv

    def tearDown(self):
        sys.argv = self._old_sys_argv

    def _set_cli_args(self, args):
        sys.argv = ['facio', ] + args
        self.config = Config()

    def test_exit_with_no_arguments(self):
        try:
            Config()
        except SystemExit:
            assert True

    @patch('facio.config.ConfigFile.path', new_callable=PropertyMock)
    def test_cfg_is_not_loaded(self, mock_path):
        mock_path.return_value = '/this/does/not/exist.cfg'
        sys.argv = sys.argv + self.base_args
        c = Config()

        self.assertFalse(c.file_args.cfg_loaded)

    @patch('facio.config.ConfigFile.path', new_callable=PropertyMock)
    @patch('facio.config.blue')
    def test_cfg_is_loaded(self, mock_blue, mock_path):
        sys.argv = sys.argv + self.base_args
        mock_path.return_value = self.empty_cfg
        c = Config()
        mock_blue.assert_called_with('Loaded ~/.facio.cfg')
        self.assertTrue(c.file_args.cfg_loaded)

    def test_valid_project_name(self):
        valid_names = ['this_is_valid', 'this1is_valid', 'Thisisvalid']
        for valid_name in valid_names:
            try:
                self._set_cli_args([valid_name, ])
                self.assertEquals(self.config.project_name, valid_name)
            except:
                import ipdb
                ipdb.set_trace()

    def test_exit_on_invalid_name(self):
        invalid_names = ['this_is_not-valid', 'this_is not_valid',
                         '*this_is_not_valid']
        for invalid_name in invalid_names:
            try:
                self._set_cli_args([invalid_name, ])
            except (SystemExit, DocoptExit):
                assert True
            else:
                assert False

    def test_template_var_is_set_from_cli(self):
        self._set_cli_args(self.base_args + ['--template',
                                             self.test_tpl_path])
        self.assertEquals(self.config.template, self.test_tpl_path)

    @patch('facio.config.ConfigFile.path', new_callable=PropertyMock)
    def test_exit_if_facio_cfg_is_miss_configured(self, mock_path):
        cfgs = ['malformed_config1.cfg', 'malformed_config2.cfg']
        for cfg in cfgs:
            mock_path.return_value = self._test_cfg_path(cfg)
            self._set_cli_args(self.base_args)
            self.assertFalse(self.config.file_args.cfg_loaded)

    @patch('facio.config.ConfigFile.path', new_callable=PropertyMock)
    def test_valid_template_is_chosen_from_config(self, mock_path):
        mock_path.return_value = self._test_cfg_path('multiple_templates.cfg')
        config.input = lambda _: '2'
        try:
            self._set_cli_args(self.base_args + ['-s', ])
            self.config = Config()
            self.assertEquals(self.config.template, '/path/to/template')
        except SystemExit:
            pass  # We allow a pass here because the template path is invalid

    def test_fail_if_invalid_template_choice(self):
        config.input = lambda _: '8'
        try:
            self._set_cli_args(self.base_args + ['-s', ])
            self.config = Config()
        except SystemExit:
            assert True

    def test_value_error_raised_on_zero_template_choice(self):
        config.input = lambda _: '0'
        try:
            self._set_cli_args(self.base_args + ['-s', ])
            self.config = Config()
        except SystemExit:
            assert True

    @patch('os.path.isdir', return_value=True)
    @patch('facio.config.ConfigFile.path', new_callable=PropertyMock)
    def test_can_refernce_template_by_name_from_cli(
            self,
            mock_path,
            mock_isdir):
        mock_path.return_value = self._test_cfg_path('multiple_templates.cfg')
        try:
            self._set_cli_args(self.base_args + ['-t', 'foo'])
            self.config = Config()
            self.assertEquals(self.config.template, '/path/to/template/foo')
        except SystemExit:
            assert False

    @patch('facio.config.ConfigFile.path', new_callable=PropertyMock)
    def test_can_refernce_template_by_name_from_cli_invalid(self, mock_path):
        mock_path.return_value = self._test_cfg_path('multiple_templates.cfg')
        try:
            self._set_cli_args(self.base_args + ['-t', 'not_valid_name'])
            Config()
        except SystemExit:
            assert True

    def test_cache_django_secret_key(self):
        sys.argv = sys.argv + self.base_args
        self.config = Config()
        key = self.config.django_secret_key
        self.assertEquals(key, self.config.generated_django_secret_key)

    def test_return_cached_version_of_secret_key(self):
        sys.argv = sys.argv + self.base_args
        self.config = Config()
        self.config.generated_django_secret_key = 'this_is_cached'
        self.assertEquals(self.config.django_secret_key, 'this_is_cached')
