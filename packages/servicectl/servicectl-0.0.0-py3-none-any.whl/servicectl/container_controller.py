#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 Pavle Portic <pavle.portic@tilda.center>
#
# Distributed under terms of the BSD-3-Clause license.

from copy import deepcopy

from docker.models.containers import Container
from docker.errors import NotFound

from .docker_controller import DockerController
from .exceptions import InternalDockerError


class ContainerController(DockerController):
	def __init__(self, controller: DockerController = None):
		if controller is None:
			super(ContainerController, self).__init__()
		else:
			self.client = controller.client

	def get_active_containers(self, tracked_services: list) -> list:
		try:
			containers = self.client.containers.list(all=True)
		except NotFound as e:
			raise InternalDockerError(e)

		services = deepcopy(tracked_services)
		for service in services:
			service['containers'] = [
				{
					'id': container.id,
					'short_id': container.short_id,
					'name': container.name,
					'status': container.status,
				} for container in containers if container.name.startswith(service['name'])
			]

		return services

	def get_container(self, container_id: str) -> Container:
		return self.client.containers.get(container_id)

	def exec_command(self, container: Container, command: str) -> tuple:
		code, output = container.exec_run(['sh', '-c', command])

		return code, output.decode('UTF-8')

	def get_logs(self, container: Container, tail: int = 1000) -> str:
		return container.logs(tail=tail).decode('UTF-8')
