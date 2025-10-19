from typing import Self

import numpy as np

from stage import Stage
from visualize import Visualizable


class GridMap(Visualizable, np.ndarray):
    """
    ステージの障害物をグリッドマップとして表現するクラス

    Attributes:
        cell_size (int): グリッドの1マスのサイズ（mm）
    """

    cell_size: int

    def __new__(
        cls,
        stage: Stage,
        cell_size: int,
        *args,
        **kwargs,
    ) -> Self:
        x_cells = stage.x_size // cell_size
        y_cells = stage.y_size // cell_size
        instance = np.zeros((y_cells, x_cells), dtype=np.uint8).view(cls)

        instance.cell_size = cell_size
        instance._set_obstacles(stage)

        return instance

    def _set_obstacles(self, stage: Stage) -> None:
        """
        ステージの障害物情報をグリッドマップに設定するメソッド

        Args:
            stage (Stage): ステージオブジェクト
        """
        # ステージの外壁
        self[:, 0] = 1
        self[:, -1] = 1
        self[0, :] = 1
        self[-1, :] = 1

        # 壁
