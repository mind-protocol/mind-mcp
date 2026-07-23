from runtime.l4 import citizen_registry


class Result:
    def __init__(self, rows):
        self.result_set = rows


class Graph:
    def __init__(self):
        self.queries = []

    def query(self, query, params):
        self.queries.append((query, params))
        if "h.tg_user_id" in query:
            return Result([["reyno"]])
        if "bilateral_bond" in query:
            return Result([["nlr_ai"]])
        raise AssertionError(query)


def test_username_collision_falls_back_to_stable_human_telegram_id(monkeypatch):
    graph = Graph()
    monkeypatch.setattr(citizen_registry, "_graph", lambda: graph)
    monkeypatch.setattr(
        citizen_registry,
        "get_citizen",
        lambda handle: {
            "handle": handle,
            "type": "citizen",
        } if handle == "nlr_ai" else None,
    )
    citizen_registry._cache.clear()

    assert citizen_registry.citizen_for_human(
        user_id="1864364329",
        username="nlr_ai",
    ) == "nlr_ai"
    assert graph.queries[0][1] == {"v": "1864364329"}


def test_verified_human_username_remains_the_preferred_identity(monkeypatch):
    graph = Graph()
    monkeypatch.setattr(citizen_registry, "_graph", lambda: graph)
    monkeypatch.setattr(
        citizen_registry,
        "get_citizen",
        lambda handle: {
            "handle": handle,
            "type": "human",
        } if handle == "reyno" else None,
    )
    citizen_registry._cache.clear()

    assert citizen_registry.citizen_for_human(
        user_id="1864364329",
        username="reyno",
    ) == "nlr_ai"
    assert len(graph.queries) == 1
    assert "bilateral_bond" in graph.queries[0][0]
