import ast


def ast_parse_expr(code: str) -> ast.expr:
    stmt = ast.parse(code).body[0]
    assert isinstance(stmt, ast.Expr)
    return stmt.value


def ast_parse_call(code: str) -> ast.Call:
    expr = ast_parse_expr(code)
    assert isinstance(expr, ast.Call)
    return expr
