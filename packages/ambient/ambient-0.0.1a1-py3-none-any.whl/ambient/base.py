"""Base classes."""

from dataclasses import dataclass, field, fields
from uuid import UUID, uuid4
from typing import ClassVar, Dict, Type


@dataclass
class BaseElement:
    """Implements required generic functionality for all elements."""

    factory: ClassVar[Dict[str, Type]] = {}

    guid: UUID = field(default_factory=uuid4)

    def __init_subclass__(cls, **kwargs):
        """Register the subclass for file loading."""
        super().__init_subclass__(**kwargs)
        BaseElement.factory[cls.__name__] = cls

    def resolve_references(
        self, references: Dict[UUID, "BaseElement"]
    ):  # pylint: disable=no-self-use
        """Resolve loaded guids within the simulation."""

    def get_dependencies(self):
        """Return the guids of element dependencies."""

    def get_outputs(self):
        """Return the names of all public fields/properties.

        These can be used by dependent elements.
        """
        outputs = [f.name for f in fields(self) if not f.name.startswith("_")]
        outputs += [
            prop for prop, _ in vars(self).items() if isinstance(prop, property)
        ]

        return outputs

    def _resolve_element(self, guid: str, references: Dict[UUID, "BaseElement"]):
        return references[UUID(guid)]

    def update(self):
        """Update the element."""


class BaseElementTemplate(BaseElement):
    """Class for templating."""

    def resolve_templates(
        self, references: Dict[UUID, BaseElement]
    ):  # pylint: disable=no-self-use
        """Return a list of templated elements."""
