from agents.tools.clustering_tools import cluster_complaints


def test_cluster_complaints_empty():
    result = cluster_complaints([])
    assert result == []
