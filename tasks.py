import re
import subprocess
from pathlib import Path

from invoke import task

ROOT = Path(__file__).parent


@task
def lint(ctx):
    """Lint code."""
    ctx.run("black --check typpy tests --exclude tests/cases/sqlalchemy")
    ctx.run("flake8 typpy tests --exclude tests/cases/sqlalchemy --max-line-length 100")


@task
def format_code(ctx):
    """Format code."""
    ctx.run("black typpy tests --exclude tests/cases/sqlalchemy")


@task
def test(ctx):
    """Run tests."""
    ctx.run("pytest tests")


@task
def check(ctx):
    """Run linting tools and tests."""
    lint(ctx)
    test(ctx)


def get_version():
    setup = (ROOT / "setup.py").read_text()
    version = re.search(r'version="(.+)"', setup).group(1)
    return map(int, version.split("."))


def get_commit_types():
    tag = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0", "@^"],
        stdout=subprocess.PIPE,
        check=True,
    ).stdout.strip()
    log = subprocess.run(
        ["git", "log", "--oneline", f"{tag.decode()}..HEAD"],
        stdout=subprocess.PIPE,
        check=True,
    ).stdout.decode()

    commit_types = [
        "breaking_change"
        if "BREAKING CHANGE" in line
        else line.split()[1].replace(":", "")
        for line in log.split("\n")
        if line.strip()
    ]
    return [ct for ct in commit_types if ct in ("breaking_change", "feat", "fix")]


def increment_version(version, commit_types):
    major, minor, patch = version

    if "breaking_change" in commit_types:
        major += 1
    elif "feat" in commit_types:
        minor += 1
    elif "patch" in commit_types:
        patch += 1

    return major, minor, patch


def update_version(version):
    setup_path = ROOT / "setup.py"
    setup = setup_path.read_text()
    setup = re.sub(r'version="(.+)"', f'version="{version}"', setup)
    setup_path.write_text(setup)


def tag(ctx, version):
    ctx.run("git add .")
    ctx.run(f"git commit -m 'Release v{version}'")
    ctx.run(f"git tag v{version}")


def publish(ctx, token):
    ctx.run("python setup.py sdist bdist_wheel")
    ctx.run("twine check dist/*")
    ctx.run(
        f"twine upload --repository-url https://upload.pypi.org/legacy/ dist/* "
        f"-u __token__ -p {token}"
    )


@task
def release(ctx, token):
    """Release package. For use in CI."""
    version = get_version()
    commit_types = get_commit_types()

    new_version = increment_version(version, commit_types)
    new_version_str = ".".join(map(str, new_version))

    update_version(new_version_str)
    tag(ctx, new_version_str)
    publish(ctx, token)
