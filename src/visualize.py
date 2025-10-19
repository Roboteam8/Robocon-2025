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

    def update(self, dt: float) -> None:
        """
        オブジェクトの状態を更新する抽象メソッド

        Args:
            dt (float): 経過時間 (秒)
        """


VISUALIZABLES: list[Visualizable] = []


def visualize(frame_rate: int) -> None:
    """
    Matplotlibを使用してオブジェクトを可視化する関数

    Args:
        frame_rate (int): フレームレート (FPS)
    """
    fig, ax = plt.subplots()

    for visualizable in VISUALIZABLES:
        visualizable.visualize(ax)
        visualizable.animate(ax)  # 初期描画

    def update(_: int) -> list[Artist]:
        artists = []
        for visualizable in VISUALIZABLES:
            visualizable.update(1 / frame_rate)
            artists.extend(visualizable.animate(ax))
        return artists

    _ = FuncAnimation(
        fig, update, frames=range(100), blit=True, interval=1000 / frame_rate
    )

    plt.show()
