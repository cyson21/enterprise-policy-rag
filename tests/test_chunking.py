from app.chunking import chunk_text


def test_chunk_text_preserves_paragraph_order_and_metadata():
    content = "Intro policy.\n\nRemote work requires VPN.\n\nSecurity review is mandatory."

    chunks = chunk_text(content, max_chars=32)

    assert [chunk.index for chunk in chunks] == [0, 1, 2]
    assert [chunk.text for chunk in chunks] == [
        "Intro policy.",
        "Remote work requires VPN.",
        "Security review is mandatory.",
    ]


def test_chunk_text_rejects_empty_content():
    try:
        chunk_text(" \n\t ")
    except ValueError as exc:
        assert "empty" in str(exc)
    else:
        raise AssertionError("empty content should be rejected")
