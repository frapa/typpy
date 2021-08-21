from invoke import task


@task
def lint(ctx):
    ctx.run("black --check typy tests")
    ctx.run("flake8 typy tests")


@task
def format_code(ctx):
    ctx.run("black typy tests")


@task
def test(ctx):
    ctx.run("pytest tests")


@task
def check(ctx):
    lint(ctx)
    test(ctx)
