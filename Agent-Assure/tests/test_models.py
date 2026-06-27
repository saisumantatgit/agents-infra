from scripts.ground_check import load_store, resolve, Verdict, ClaimKind

def test_load_store_indexes_by_source_id(tmp_path):
    p = tmp_path / "s.jsonl"
    p.write_text('{"source_id":"S1","url":"http://a","file_path":null,"fetched_at":"2026-06-20T00:00:00Z","tool":"exa.web_fetch_exa","content_sha256":"x","text":"Redis handles 100K ops","full_text_source":"verbatim","captured_via":"inline","query_provenance":"q1"}\n')
    store = load_store(str(p))
    assert set(store.keys()) == {"S1"}
    assert store["S1"].full_text_source == "verbatim"

def test_resolve_marker_to_source(tmp_path):
    p = tmp_path / "s.jsonl"; p.write_text('{"source_id":"S1","url":null,"file_path":null,"fetched_at":"t","tool":"Read","content_sha256":"x","text":"t","full_text_source":"verbatim","captured_via":"inline","query_provenance":"q"}\n')
    store = load_store(str(p))
    assert resolve("[S1]", store).source_id == "S1"
    assert resolve("[S9]", store) is None
    assert Verdict.UNVERIFIED_CITATION.value == "UNVERIFIED_CITATION"
    assert ClaimKind.NON_CLAIM.value == "NON_CLAIM"
