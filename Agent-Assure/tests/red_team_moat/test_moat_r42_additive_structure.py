"""RED-TEAM-R42 structural guard: every R40 addition must be strictly
additive, so the branch refuses whenever origin/main refuses, for every input.

R40 broke that by widening `_has_strong_denial` IN PLACE. The widened
predicate was also read NEGATIVELY (main's `_strong_tokens` clearing step),
and sources main refuses certified PASS 100.0 (B1/B2,
test_moat_r42_heading_seam.py). The fix computes main's denial verdict with
main's code and ORs the R40 reading on top (`_match_denied`). These tests pin
that structure so a future in-place widening fails here, not in a red-team
round:

1. The MAIN denial path -- every module-level function reachable from
   `_source_unit_contexts` and `_unit_denied`, plus the value of every
   module-level constant those functions read -- is pinned by digest. The pin
   was computed from origin/main 746f337's `scripts/ground_check.py` with
   this same digest function, so it certifies the path is AST-identical to
   main's (docstrings excluded). If this fails, a function or word list on
   main's path changed. That is allowed only when the same change is on
   origin/main; an R40-style addition belongs in an `_r40` function instead.
2. The main path reaches no R40 name.
3. `_match_denied` reads main's verdict first and ORs the R40 reading, and
   the R40 reading is entered only through `_match_denied` / `_denial_units`.
"""
from __future__ import annotations

import ast
import hashlib
import re
from pathlib import Path

GATE = Path(__file__).resolve().parents[2] / "scripts" / "ground_check.py"

MAIN_PATH_ROOTS = ("_source_unit_contexts", "_unit_denied")
# Digest of origin/main 746f337 scripts/ground_check.py under `main_path_digest`.
MAIN_PATH_DIGEST = "36d4617bf2f10eaaa9230b8b76a17a5a6e98ab7de10d5f2061a943befa1f328b"
# Names that exist only for the R40 reading. Any name containing "r40" counts too.
R40_ONLY_NAMES = frozenset({
    "_falsity_construction", "_forward_free_relative", "_event_negation_points",
    "_long_line_points", "_trailing_denied", "_comparison_view", "_view_unit_contexts",
    "_view_token", "_align_tokens", "_match_denied", "_denial_units", "_DenialUnit",
})


def _module_defs(tree: ast.Module) -> tuple[dict[str, ast.AST], dict[str, ast.Module]]:
    """Module-level functions/classes by name, and for each module-level
    constant EVERY statement that binds or rebinds it (Assign, AnnAssign,
    AugAssign), in source order, so a later `_X |= {...}` is pinned too.

    CEILING: a mutation through a method call (`_SOME_DICT.update(...)`) or
    from another module is not seen; the main-path word lists are frozensets
    (immutable), so only `_DENIAL_CONFUSABLES` (a translate table) could be.
    Upgrade path: digest the runtime values as well."""
    funcs: dict[str, ast.AST] = {}
    consts: dict[str, list[ast.AST]] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            funcs[node.name] = node
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    consts.setdefault(t.id, []).append(node)
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign)) and isinstance(node.target, ast.Name):
            consts.setdefault(node.target.id, []).append(node)
    return funcs, {k: ast.Module(body=v, type_ignores=[]) for k, v in consts.items()}


def _names(node: ast.AST) -> set[str]:
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def _closure(tree: ast.Module, roots: tuple[str, ...]) -> tuple[list[str], list[str]]:
    """(functions, constants) reachable from *roots*. Classes are data
    containers and are not followed (the R40 `suffix` field on `_UnitContext`
    is read only by the R40 reading)."""
    funcs, consts = _module_defs(tree)
    seen_f: set[str] = set()
    seen_c: set[str] = set()
    todo = list(roots)
    while todo:
        name = todo.pop()
        if name in seen_f or name not in funcs or isinstance(funcs[name], ast.ClassDef):
            continue
        seen_f.add(name)
        for ref in _names(funcs[name]):
            if ref in funcs:
                todo.append(ref)
            elif ref in consts:
                seen_c.add(ref)
    # Constants built from other constants: follow their names too.
    todo_c = list(seen_c)
    while todo_c:
        for ref in _names(consts[todo_c.pop()]):
            if ref in consts and ref not in seen_c:
                seen_c.add(ref)
                todo_c.append(ref)
            elif ref in funcs and not isinstance(funcs[ref], ast.ClassDef) and ref not in seen_f:
                raise AssertionError(f"constant on the main path calls a function: {ref}")
    return sorted(seen_f), sorted(seen_c)


def _strip_docstring(node: ast.AST) -> ast.AST:
    node = ast.parse(ast.unparse(node)).body[0]
    body = getattr(node, "body", None)
    if (body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)):
        node.body = body[1:] or [ast.Pass()]
    return node


def main_path_digest(source: str) -> str:
    """sha256 over the docstring-free AST of every main-path function and the
    source AST of every main-path constant. Pure."""
    tree = ast.parse(source)
    funcs, consts = _module_defs(tree)
    fnames, cnames = _closure(tree, MAIN_PATH_ROOTS)
    h = hashlib.sha256()
    for name in fnames:
        h.update(f"F {name} {ast.dump(_strip_docstring(funcs[name]))}\n".encode())
    for name in cnames:
        h.update(f"C {name} {ast.dump(consts[name])}\n".encode())
    return h.hexdigest()


def _is_r40(name: str) -> bool:
    return "r40" in name.lower() or name in R40_ONLY_NAMES


def test_main_denial_path_is_pinned_to_origin_main() -> None:
    digest = main_path_digest(GATE.read_text(encoding="utf-8"))
    assert digest == MAIN_PATH_DIGEST, (
        "main's denial path changed (a function or constant reachable from "
        f"{MAIN_PATH_ROOTS}). Allowed only if origin/main changed the same way; "
        "an R40-style refusal belongs in an _r40 function OR'd by _match_denied. "
        f"New digest: {digest}")


def test_main_denial_path_reaches_no_r40_name() -> None:
    tree = ast.parse(GATE.read_text(encoding="utf-8"))
    fnames, cnames = _closure(tree, MAIN_PATH_ROOTS)
    leaked = [n for n in fnames + cnames if _is_r40(n)]
    assert not leaked, f"main's denial path reaches R40 names: {leaked}"


def test_match_denied_ors_r40_onto_main_verdict() -> None:
    tree = ast.parse(GATE.read_text(encoding="utf-8"))
    funcs, _ = _module_defs(tree)
    body = _strip_docstring(funcs["_match_denied"]).body
    assert len(body) == 1 and isinstance(body[0], ast.Return), "_match_denied must be one OR expression"
    expr = body[0].value
    assert isinstance(expr, ast.BoolOp) and isinstance(expr.op, ast.Or), "_match_denied must be an OR"
    first = expr.values[0]
    assert (isinstance(first, ast.Call) and isinstance(first.func, ast.Name)
            and first.func.id == "_unit_denied"
            and isinstance(first.args[0], ast.Attribute) and first.args[0].attr == "main"), (
        "the first operand of _match_denied must be main's verdict: _unit_denied(unit.main, ...)")


def test_r40_reading_is_entered_only_through_match_denied() -> None:
    """No consumer reads an R40 context without main's verdict before it."""
    tree = ast.parse(GATE.read_text(encoding="utf-8"))
    funcs, _ = _module_defs(tree)
    allowed = {
        "_source_unit_contexts_r40": {"_denial_units", "_view_unit_contexts"},
        "_r40_match_denied": {"_match_denied"},
        "_denial_units": {"_contained_with_matching_polarity", "_anchor_sentence_covers"},
    }
    for target, callers in allowed.items():
        actual = {name for name, node in funcs.items() if target in _names(node) and name != target}
        assert actual <= callers, f"{target} is read by {sorted(actual - callers)}, outside {sorted(callers)}"
    # The two consumers must decide through _match_denied, never _unit_denied/_unit_denied_r40.
    for consumer in allowed["_denial_units"]:
        names = _names(funcs[consumer])
        assert "_match_denied" in names, consumer
        assert not names & {"_unit_denied", "_unit_denied_r40", "_r40_match_denied"}, consumer
    assert re.search(r"\bdef _match_denied\(unit: _DenialUnit", GATE.read_text(encoding="utf-8"))
