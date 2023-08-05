#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 Pavle Portic <pavle.portic@tilda.center>
#
# Distributed under terms of the BSD-3-Clause license.

import time
from typing import List
from datetime import datetime

from docker import errors as docker_errors
from docker.models.services import Service
from docker.models.images import Image

from . import logger
from .docker_controller import DockerController
from .exceptions import (
	ImageNotFound,
	ServiceUpdateError,
	StackRevertFailed,
)


class ServiceController(DockerController):
	def __init__(self, controller: DockerController = None):
		if controller is None:
			super(ServiceController, self).__init__()
		else:
			self.client = controller.client

	def _get_active_services(self) -> List[Service]:
		""" Get a list of all docker services running on the swarm
		"""
		return self.client.services.list()

	def _init_image_mappings(self, tracked_services: List[dict], services_to_update: List[str]) -> None:
		active_services = self._get_active_services()
		active_service_names = [service.name for service in active_services]
		service_names = set(services_to_update) & set(active_service_names)
		service_names = list(service_names)
		self.image_mappings = {
			service.name: {
				'repository': service.repository,
				'tag': service.tag,
			} for service in tracked_services if service.name in service_names
		}

	def _backup_images(self) -> None:
		""" Back up images in case the services need to be reverted
		"""
		try:
			for service in self.image_mappings:
				image_name = self.image_mappings[service]
				image = self.client.images.get(f'{image_name["repository"]}:{image_name["tag"]}')
				backup_tag = f'{image_name["tag"]}-previous'
				image.tag(image_name['repository'], tag=backup_tag)
		except docker_errors.ImageNotFound as e:
			logger.error(e)
			raise ImageNotFound('No backup images were created')

	def _pull_images(self) -> None:
		""" Pull the latest docker images for every service
		"""
		try:
			for service in self.image_mappings:
				image = self.image_mappings[service]
				self.client.images.pull(repository=image['repository'], tag=image['tag'])
		except docker_errors.NotFound:
			raise ImageNotFound('Failed to pull the image')

	def _wait_for_service_update(self, service: Service, now: datetime) -> None:
		""" Wait until the service has finished or failed updating
		"""
		while True:
			time.sleep(1)
			service.reload()
			updated_at = service.attrs['UpdatedAt'].split('.')[0]
			updated_at = datetime.strptime(updated_at, '%Y-%m-%dT%H:%M:%S')
			if updated_at > now and service.attrs['UpdateStatus']['State'] != 'updating':
				break

	def _revert_services(self, updated_services: List[Service], failed_service: str) -> None:
		""" Revert all previously updated services to the previously backed up images
		"""
		for service in updated_services:
			image = self.image_mappings[service.name]
			image = f'{image["repository"]}:{image["tag"]}-previous'
			try:
				self.update_service(service, image)
			except docker_errors.APIError as e:
				logger.critical(e)
				raise StackRevertFailed(e)
			except ServiceUpdateError as e:
				logger.error(f'Failed to revert service {e}')
				raise StackRevertFailed(e)

		return failed_service

	def set_services_status(self, tracked_services: List[dict]) -> None:
		""" Set the active status for each tracked service based on if it's running
		"""
		active_services = self._get_active_services()
		for service in tracked_services:
			if any(active_service.name == service['name'] for active_service in active_services):
				service['active'] = True
			else:
				service['active'] = False

	def update_service(self, service: Service, image: Image) -> None:
		""" Force update a single docker service
		"""
		now = datetime.utcnow()
		service.update(image=image, force_update=True)
		self._wait_for_service_update(service, now)
		update_state = service.attrs['UpdateStatus']['State']
		if update_state != 'completed':
			raise ServiceUpdateError(service.name)

	def update_stack(self, tracked_services: list, services_to_update: list) -> dict:
		""" Atomically update all services passed in services_to_update.

		Pulls the latest images while backing up the old ones.
		Force updates all services and waits until it completes.
		In case of an update error, the whole stack gets reverted
		to the previous images
		"""
		active_services = self.client.services.list()
		self._init_image_mappings(tracked_services, services_to_update)
		self._backup_images()
		self._pull_images()
		updated_services = []

		for service in active_services:
			if service.name not in self.image_mappings:
				continue

			image = self.image_mappings[service.name]
			image = f'{image["repository"]}:{image["tag"]}'
			try:
				updated_services.append(service)
				self.update_service(service, image)
			except docker_errors.APIError as e:
				logger.critical(e)
				return False, self._revert_services(updated_services, service.name)
			except ServiceUpdateError as e:
				logger.warning(f'Failed to update service {e}')
				return False, self._revert_services(updated_services, service.name)

		return True, None
