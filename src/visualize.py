from abc import ABCMeta
from typing import Callable

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


def visualize(
    frame_rate: int, additional_plot: Callable[[Axes], None] = lambda _: None
) -> None:
    """
    Matplotlibを使用してオブジェクトを可視化する関数

    Args:
        frame_rate (int): フレームレート (FPS)
        additional_plot (Callable[[Axes], None], optional): 追加の描画を行う関数. デフォルトは空の関数.
    """
    fig, ax = plt.subplots()

    for visualizable in VISUALIZABLES:
        visualizable.visualize(ax)

    additional_plot(ax)

    def update(_: int) -> list[Artist]:
        animated = []
        for visualizable in VISUALIZABLES:
            animated.extend(visualizable.animate(ax))
        return animated

    _ = FuncAnimation(
        fig, update, frames=range(100), blit=True, interval=1000 / frame_rate
    )

    plt.show()
