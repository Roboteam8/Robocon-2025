from stage import Area


def generate_path(start: Area, end: Area) -> list[tuple[float, float]]:
    """
    エリアからエリアまでの経路を生成する関数

    Args:
        start (Area): スタートエリア
        end (Area): ゴールエリア

    Returns:
        list[tuple[float, float]]: 経路上の座標リスト
    """
    sx, sy = (
        start.position[0] + start.size / 2,
        start.position[1] + start.size / 2,
    )
    ex, ey = (end.position[0] + end.size / 2, end.position[1] + end.size / 2)

    path = [(sx, sy)]

    if min(sx, ex) < 1000 < max(sx, ex):
        path.append((sx, 1500))
        path.append((ex, 1500))
    elif sx != ex and sy != ey:
        path.append((ex, sy))

    path.append((ex, ey))

    return path
