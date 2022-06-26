# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
import abc
import dataclasses
import typing as t

from googleapiclient import discovery

from tlab_google import credentials


@dataclasses.dataclass()  # type: ignore[misc]
class AbstractAPI(abc.ABC):
    """Abstract class for Google API."""
    credentials: credentials.Credentials
    """Credentials for the Google API."""
    version: str | None = None
    """The version of the Google API."""

    @property
    @abc.abstractmethod
    def service_name(self) -> str:
        """The name of the Google service."""


def build_service(api: AbstractAPI) -> t.Any:
    """Construct a Resource for interacting with an API.

    Parameters
    ----------
    api : tlab_google.abstract.AbstractAPI
        An API to interact.

    Returns
    -------
    Any
       A Resource object with methods for interacting with the service.
    """
    return discovery.build(
        serviceName=api.service_name,
        version=api.version,
        credentials=api.credentials._credentials
    )
