#!/usr/bin/env python3
#
# Copyright (C) 2024 Denis <denis@nzbget.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with the program.  If not, see <http://www.gnu.org/licenses/>.
#


import sys
from os.path import dirname
import os
import subprocess
import unittest
import shutil
import json

POSTPROCESS_SUCCESS=93
POSTPROCESS_NONE=95
POSTPROCESS_ERROR=94

root = dirname(__file__)
test_data_dir = root + '/test_data/'
tmp_dir = root + '/tmp/'
dst_dir = root + '/tmp/dst/'
dwn_dir = root + '/tmp/dwn/'
test_file = 'movie.mp4'

host = '127.0.0.1'
username = 'TestUser'
password = 'TestPassword'
port = '6789'

def get_python(): 
	if os.name == 'nt':
		return 'python'
	return 'python3'

def run_script():
	sys.stdout.flush()
	proc = subprocess.Popen([get_python(), root + '/EasySort.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ.copy())
	out, err = proc.communicate()
	proc.pid
	ret_code = proc.returncode
	return (out.decode(), int(ret_code), err.decode())

def set_defaults_env():
	# NZBGet global options
	os.environ['NZBOP_CONTROLPORT'] = port
	os.environ['NZBOP_CONTROLIP'] = host
	os.environ['NZBOP_CONTROLUSERNAME'] = username
	os.environ['NZBOP_CONTROLPASSWORD'] = password
	os.environ['NZBOP_NZBLOG'] = tmp_dir + '/log.txt'
	os.environ['NZBPP_TOTALSTATUS'] = 'SUCCESS'
	os.environ['NZBPO_PASSACTION'] = 'PASSACTION'

	# script options
	os.environ['NZBPO_OVERWRITE'] = 'yes'
	os.environ['NZBPO_CLEANUP'] = 'yes'
	os.environ['NZBPO_PREVIEW'] = 'no'
	os.environ['NZBPO_VERBOSE'] = 'no'
	os.environ['NZBPP_TOTALSTATUS'] = 'SUCCESS'
	os.environ['NZBPP_DIRECTORY'] = dwn_dir
	os.environ['NZBNA_NZBNAME'] = 'TestNZB'
	os.environ['NZBOP_TEMPDIR'] = tmp_dir
	os.environ['NZBPO_DESTDIR'] = dst_dir
	os.environ['NZBPO_EXTENSIONS'] = '.mp4'
	os.environ['NZBPP_NZBNAME'] = test_file

class Tests(unittest.TestCase):

	def test_do_nothing_if_file_too_small(self):
		os.mkdir(tmp_dir)
		os.mkdir(dwn_dir)
		shutil.copyfile(test_data_dir + test_file, dwn_dir + test_file)
		set_defaults_env()
		os.environ['NZBPO_MINSIZE'] = '1000'
		[_, code, _] = run_script()
		shutil.rmtree(tmp_dir)
		self.assertEqual(code, POSTPROCESS_NONE)

	def test_move_file(self):
		os.mkdir(tmp_dir)
		os.mkdir(dwn_dir)
		shutil.copyfile(test_data_dir + test_file, dwn_dir + test_file)
		set_defaults_env()
		os.environ['NZBPO_MINSIZE'] = '0'
		[_, code, _] = run_script()
		shutil.rmtree(tmp_dir)
		self.assertEqual(code, POSTPROCESS_SUCCESS)

	def test_manifest(self):
		with open(root + '/manifest.json', encoding='utf-8') as file:
			try:
				json.loads(file.read())
			except ValueError as e:
				self.fail('manifest.json is not valid.')


if __name__ == '__main__':
	unittest.main()
