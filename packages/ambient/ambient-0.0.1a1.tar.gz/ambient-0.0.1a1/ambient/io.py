"""Input output module."""

import json
from dataclasses import fields
from uuid import UUID

from deltaq.base import BaseElement
from deltaq.simulation import Simulation


def _field_dict(obj):
    return {
        "type": type(obj).__name__,
        "data": {
            f.name: getattr(obj, f.name)
            for f in fields(obj)
            if not f.name.startswith("_")
        },
    }


class SimulationEncoder(json.JSONEncoder):
    """Encode simulations as JSON."""

    def default(self, o):  # pylint: disable=method-hidden
        """Handle simulation specific classes."""
        if isinstance(o, UUID):
            return f"{o.urn}"
        if isinstance(o, Simulation):
            sim = _field_dict(o)
            sim["data"]["elements"] = {
                e.guid.urn: _field_dict(e) for e in o.elements.values()
            }
            return sim
        if isinstance(o, BaseElement):
            return o.guid

        return json.JSONEncoder.default(self, o)


def simulation_decoder(dct):
    """Rebuild simulation classes on import."""
    if "guid" in dct:
        dct["guid"] = UUID(dct["guid"])

    if "type" in dct and "data" in dct:
        factory = BaseElement.factory[dct["type"]]
        return factory(**dct["data"])

    return dct
