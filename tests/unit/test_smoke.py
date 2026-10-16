import veriquery


def test_package_imports() -> None:
    assert veriquery.__version__ == "0.0.1"


def test_subpackages_import() -> None:
    import veriquery.agent
    import veriquery.agent.llm
    import veriquery.api
    import veriquery.catalog
    import veriquery.common
    import veriquery.composer
    import veriquery.executor
    import veriquery.mcp
    import veriquery.verifier

    assert veriquery.verifier.__doc__
