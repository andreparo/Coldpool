from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Disk:
    """A physical storage disk available for artifact copy placement."""
