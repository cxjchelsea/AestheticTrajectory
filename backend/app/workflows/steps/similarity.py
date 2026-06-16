import math


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        raise ValueError("Cosine similarity requires non-empty vectors")
    if len(left) != len(right):
        raise ValueError("Cosine similarity requires vectors with the same dimension")

    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        raise ValueError("Cosine similarity requires non-zero vectors")

    dot_product = sum(left_value * right_value for left_value, right_value in zip(left, right))
    return dot_product / (left_norm * right_norm)


def connected_components(edges: list[tuple[str, str]]) -> list[list[str]]:
    neighbors: dict[str, set[str]] = {}
    for left, right in edges:
        neighbors.setdefault(left, set()).add(right)
        neighbors.setdefault(right, set()).add(left)

    components: list[list[str]] = []
    seen: set[str] = set()
    for node in neighbors:
        if node in seen:
            continue

        stack = [node]
        component: list[str] = []
        seen.add(node)
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbor in neighbors.get(current, set()):
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)

        if len(component) >= 2:
            components.append(sorted(component))

    return components
