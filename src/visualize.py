from abc import ABCMeta

from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.artist import Artist
from matplotlib.axes import Axes


class _InstanceTracker(ABCMeta):
    """
    インスタンスを追跡するためのメタクラス
    """

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        VISUALIZABLES.append(instance)
        return instance


class Visualizable(metaclass=_InstanceTracker):
    """
    MatplotlibのAxesにオブジェクトを描画するための抽象基底クラス
    """

    def visualize(self, ax: Axes) -> None:
        """
        MatplotlibのAxesにオブジェクトを描画する抽象メソッド

        Args:
            ax (Axes): 描画先のMatplotlibのAxesオブジェクト
        """

    def animate(self, ax: Axes) -> list[Artist]:
        """
        アニメーション用にMatplotlibのAxesにオブジェクトを描画する抽象メソッド

        Args:
            ax (Axes): 描画先のMatplotlibのAxesオブジェクト

        Returns:
            list[Artist]: 描画したオブジェクトのリスト
        """
        return []


VISUALIZABLES: list[Visualizable] = []


def visualize() -> None:
    fig, ax = plt.subplots()

    for visualizable in VISUALIZABLES:
        visualizable.visualize(ax)
        visualizable.animate(ax)  # 初期描画

    def update(_: int) -> list[Artist]:
        artists = []
        for visualizable in VISUALIZABLES:
            artists.extend(visualizable.animate(ax))
        return artists

    _ = FuncAnimation(
        fig, update, frames=range(100), blit=True, interval=1000 / 30
    )  # 30 FPS

    plt.show()
