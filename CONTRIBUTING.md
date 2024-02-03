# Contributing

Welcome to the RAG Core community! Whether you are fixing a bug, improving documentation, or implementing a new feature, your contributions are highly valued. To ensure the codebase's maintainability, please adhere to the guidelines outlined below.

For detailed information about the project, consult the [documentation](https://daved01.github.io/ragcore/).

## Reporting Issues

If you discover a bug or have a feature request, please open an issue [here](https://github.com/daved01/ragcore/issues). When reporting a bug, include a descriptive title, clear description, relevant information, and a code sample or executable test case that demonstrates the unexpected behavior.

## Opening a Pull Request

Before opening a pull request, ensure that your code in the `ragcore` directory passes all quality checks. New code should be covered by tests and documented with comments where applicable. In most cases, type hints should be added as well. Keeping pull requests small by changing only relevant code simplifies reviews and debugging.

You can check your code with the following commands:

```bash
pylint ragcore/
black ragcore/
mypy ragcore/
```

Use Conventional Commits: Follow conventional commits for meaningful and standardized commit messages.

OLD STUFF
---------------------

Whether you are fixing a bug, improving documentation, or implementing a new feature, your contributions are very much appreciated! To keep the codebase maintainable, please follow the guidelines below.

If you found a bug, please report it [here](https://github.com/daved01/ragcore/issues). Be sure to include a title and clear description, as much relevant information as possible, and a code sample or an executable test case demonstrating the expected behavior that is not occurring.

For detailed information about the project please see the [documentation](https://daved01.github.io/ragcore/).

## Opening a PR

To keep the codebase maintainable, please follow a few guidelines regarding code and commit messages. A pull request should have

+ Add tests for new code

+ Pass quality checks

+ Keep pull requests small

+ Use Conventional Commits

Before opening a PR, please make sure that your code in `ragcore` passes all quality checks. You can check your code before opening a PR with the commands

```bash
pylint ragcore/
black ragcore/
mypy ragcore/
```

New code must be covered by tests and documented with comments where applicable. In most cases type hints should be added as well. And please keep pull requests small by changing only relevant code, as this simplifies reviews and debugging if something goes wrong in the future.

### Conventional Commits

Please use [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) with the following commit elements:

**feat:** A "feature" type commit indicates the introduction of a new feature or enhancement to the project.

**fix:** A "fix" type commit indicates the correction of a bug or issue in the codebase.

**chore:** A "chore" commit is used for routine maintenance or housekeeping tasks, such as dependency updates, build system modifications, or other non-functional changes.

**docs:** A "documentation" commit is used when you make changes or additions to documentation, such as README files or inline code comments.

**build:** A "build" commit is used when you make changes related to the build system, configuration, or build tooling.

Commits in PRs will be squashed into one commit. The commit title should follow the conventional commits.
