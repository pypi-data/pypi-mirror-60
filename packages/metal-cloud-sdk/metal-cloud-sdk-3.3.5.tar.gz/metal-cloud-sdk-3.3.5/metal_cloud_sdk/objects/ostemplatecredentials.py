# -*- coding: utf-8 -*-

class OSTemplateCredentials(object):
	"""
	Information needed to connect to an OS installed by an OSTemplate.
	"""

	def __init__(self):
		pass;


	"""
	User used to connect to the OS installed by the OSTemplate
	"""
	initial_user = None;

	"""
	Password of the initial_user property.
	"""
	initial_password = None;

	"""
	SSH port used to connect to the installed OS.
	"""
	initial_ssh_port = None;

	"""
	Option to change the initial_user password on the installed OS after deploy.
	"""
	change_password_after_deploy = None;

	"""
	The schema type
	"""
	type = None;
