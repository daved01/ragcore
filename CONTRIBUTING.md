# Contributing

Welcome to the RAG Core community! Whether you are fixing a bug, improving documentation, or implementing a new feature, your contributions are highly valued. To ensure the codebase's maintainability, please adhere to the guidelines outlined below.

For detailed information about the project, consult the [documentation](https://daved01.github.io/ragcore/).

## Reporting Issues

If you discover a bug or have a feature request, please open an issue [here](https://github.com/daved01/ragcore/issues). When reporting a bug, include a descriptive title, clear description, relevant information, and a code sample or executable test case that demonstrates the unexpected behavior.

## Opening a Pull Request

Before opening a pull request, ensure that your code in the `ragcore` directory passes all quality checks. New code should be covered by tests and documented with comments where applicable. In most cases, type hints should be added as well. Keeping pull requests small by changing only relevant code simplifies reviews and debugging.

If you introduce a new feature, don't forget to document it.

You can check your code with the following commands:

```bash
pylint ragcore
black ragcore
mypy ragcore
```

Commit messages in the main branch should adhere to the principles of [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/). Please note that when merging a pull request, the individual commits within the PR are squashed into one. Ensure that the PR title follows one of the following conventional commit message types:

**feat:** A "feature" type commit indicates the introduction of a new feature or enhancement to the project. Please include documentation for the feature.

**fix:** A "fix" type commit indicates the correction of a bug or issue in the codebase.

**chore:** A "chore" commit is used for routine maintenance or housekeeping tasks, such as dependency updates, build system modifications, or other non-functional changes.

**docs:** A "documentation" commit is used when you make changes or additions to documentation, such as README files, inline code comments, or the published documentation.

Using these commit message types helps maintain a clear and standardized commit history, making it easier to understand the project's development timeline.

Thank you for your contribution and following these guidelines!
