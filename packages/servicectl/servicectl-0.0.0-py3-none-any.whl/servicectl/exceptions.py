#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 Pavle Portic <pavle.portic@tilda.center>
#
# Distributed under terms of the BSD-3-Clause license.


class ServiceUpdateError(Exception):
	pass


class StackRevertFailed(Exception):
	pass


class ImageNotFound(Exception):
	pass


class InternalDockerError(Exception):
	pass
