from matplotlib.artist import Artist
from matplotlib.axes import Axes

from visualize import Visualizable


class Path(Visualizable, list[tuple[float, float]]):
    """
    経路の情報を管理するクラス
    Attributes:
        color (str): 経路の色
        active (bool): 経路が選択されているかどうか
    """

    color: str
    active: bool = False

    def __init__(
        self, start: tuple[float, float], end: tuple[float, float], color: str
    ):
        super().__init__()
        self.color = color

        sx, sy = start
        ex, ey = end

        self.append((sx, sy))

        if min(sx, ex) < 1000 < max(sx, ex):
            self.append((sx, 1500))
            self.append((ex, 1500))
        elif sx != ex and sy != ey:
            self.append((ex, sy))

        self.append((ex, ey))

    def animate(self, ax: Axes) -> list[Artist]:
        path_x, path_y = zip(*self)
        (line,) = ax.plot(
            path_x,
            path_y,
            linestyle="--",
            color=self.color,
            alpha=1 if self.active else 0.4,
        )
        return [line]
