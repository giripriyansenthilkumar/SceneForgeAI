"""
SceneForge AI - Base Generator Interface
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseProceduralGenerator(ABC):
    """
    Abstract base class for domain-specific procedural geometry generators.
    """
    category: str = "generic"

    @abstractmethod
    def build(self, spec: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Builds the 3D geometry hierarchy from the SceneSpecification.
        Returns a dictionary of generated objects and diagnostic metrics.
        """
        pass
