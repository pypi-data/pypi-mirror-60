# Contributor's Agreement
This code is licensed under the Mozilla, version 2.0 or later [LICENSE](LICENSE).

## Contributin

Contributing to the Scientific Filesystem can be as small as asking a question by
[posting an issue](https://www.github.com/vsoch/scif/issues), or
equally posting an issue to discuss a wanted feature with your fellow
developers. If you have a quick bug fix or want to contribute to the codebase,
method is via a pull request (PR) to the project's development branch. For both
cases, make sure that you properly communicate the gist of the contribution.
For a bug fix (or request to fix), please describe the issue and show
any relevant output. For a feature request (or to start discussion on a 
contribution to do so) you can talk about your thinking with regards to
possible solutions. No question, request, or idea is too small, and we are glad
to have your contribution! 

Please note we have a [code of conduct](CODE_OF_CONDUCT.md) and ask that you
follow it for all interactions with project members and users.

## Pull Requests (PRs)

### Process
1. Essential bug fix PRs should be sent to both master and development branches.
2. Small bug fix and feature enhancement PRs should be sent to development only.
3. Follow the existing code style precedent. This does not need to be strictly
   defined as there are many thousands of lines of examples. Note the lack
   of tabs anywhere in the project, parentheses and spacing, curly bracket
   locations, source code layout, variable scoping, etc. and follow the
   project's standards.
4. For any new functionality, please write a test to be added to Continuous
   Integration (Travis) to test it/
5. The project's default copyright and header have been included in any new
   source files.
6. Make sure that your code is human understandable? This means notes in the
   code, along with a style that is easy to follow. 
7. Provide a walk through in the pull request for how you would like others
   to review it. If you write good documentation, this should almost be
   unnecessary (see point 10).
8. The pull request will be reviewed by others, and the final merge must be
   done by the project lead, @vsoch.
9. Documentation must be provided if necessary (next section)


### Documentation

1. Add any changes that you have made to the [CHANGELOG](../CHANGELOG.md)
2. Be sure to add documentation to be rendered in the web docs. These are
   the markdown files in the [docs](../docs) folder, and can be previewed
   locally with `bundle exec jekyll serve`, although this is not necessary.
   Ask for help if you aren't sure where notes should go. If you have trouble,
   you can include documentation (as markdown) in the PR, and @vsoch will
   help to add it to the docs.
3. If necessary, update the README.md or any README.md files in folders.
