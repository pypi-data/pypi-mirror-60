"""
canine.backends
=================================
Contains SLURM backends for canine
"""

from .base import AbstractTransport, AbstractSlurmBackend
from .local import LocalTransport, LocalSlurmBackend
from .remote import RemoteTransport, RemoteSlurmBackend
from .gcpTransient import TransientGCPSlurmBackend
from .imageTransient import TransientImageSlurmBackend
from .dockerTransient import DockerTransientImageSlurmBackend

__all__ = [
    'LocalSlurmBackend',
    'LocalTransport',
    'RemoteSlurmBackend',
    'RemoteTransport',
    'TransientGCPSlurmBackend',
    'TransientImageSlurmBackend',
    'DockerTransientImageSlurmBackend'
]
