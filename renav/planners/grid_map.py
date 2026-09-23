"""Minimal grid representation used by the ReNav reference model."""

from __future__ import annotations
from collections.abc import Iterable
from dataclasses import dataclass, field

GridCell = tuple[int, int]

@dataclass(frozen=True)
class GridMap:
    width: int
    height: int
    obstacles: frozenset[GridCell] = field(default_factory=frozenset)

    @classmethod
    def from_obstacles(cls, width: int, height: int, obstacles: Iterable[GridCell] = ()) -> "GridMap":
        grid = cls(width, height, frozenset(obstacles))
        grid.validate()
        return grid

    def validate(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")
        for cell in self.obstacles:
            if not self.in_bounds(cell):
                raise ValueError(f"obstacle outside grid: {cell}")

    def in_bounds(self, cell: GridCell) -> bool:
        x, y = cell
        return 0 <= x < self.width and 0 <= y < self.height

    def passable(self, cell: GridCell) -> bool:
        return cell not in self.obstacles

    def neighbors4(self, cell: GridCell) -> list[GridCell]:
        x, y = cell
        candidates = [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
        return [c for c in candidates if self.in_bounds(c) and self.passable(c)]

def manhattan(a: GridCell, b: GridCell) -> int:
    return abs(a[0]-b[0]) + abs(a[1]-b[1])
