"""Simulation classes."""

from collections import deque
from dataclasses import dataclass, field
from typing import Dict
from uuid import UUID

import networkx as nx

from deltaq.base import BaseElement


@dataclass
class Simulation(BaseElement):
    """Base object holding all information for simulations."""

    name: str = ""
    elements: Dict[UUID, BaseElement] = field(default_factory=dict)
    _dg: nx.DiGraph = field(default_factory=nx.DiGraph, compare=False)

    def register_element(self, element, is_templated=False):
        """Include an element in the simulation."""
        if not isinstance(element, BaseElement):
            raise TypeError("element must be a subclass of BaseElement")

        element.is_templated = is_templated
        self.elements[element.guid] = element

    def register_elements(self, elements, is_templated=False):
        """Include a list of elements in a simulation."""
        if not all(isinstance(ele, BaseElement) for ele in elements):
            raise TypeError("all elements must be a subclass of BaseElement")

        for ele in elements:
            self.register_element(ele, is_templated=is_templated)

    def resolve_references(self):  # pylint: disable=arguments-differ
        """Resolve all element guids and recurse."""
        self.elements = {UUID(k): v for k, v in self.elements.items()}
        for ele in self.elements.values():
            ele.resolve_references(self.elements)

    def resolve_templates(self):
        """Resolve all templated elements."""
        templates = deque(
            ele for _, ele in self.elements if isinstance(ele, BaseElementTemplate)
        )

        while templates:
            template = templates.popleft()
            new_elements = template.resolve_template(self.elements)

            # add new templates for resolution
            templates.extend(
                ele for ele in new_elements if isinstance(ele, BaseElementTemplate)
            )

            # add new elements to the simulation
            self.register_elements(new_elements, is_templated=True)

    def create_dependency_graph(self):
        """Create the dependency graph."""
        for guid in self.elements:
            self._dg.add_node(guid)

        for ele in self.elements.values():
            deps = ele.get_dependencies()

            if deps is None:
                continue

            self._dg.add_edges_from((ele.guid, dep) for dep in deps)

    def evaluation_order(self):
        """Return the order for element evaluation."""
        return nx.topological_sort(self._dg)
