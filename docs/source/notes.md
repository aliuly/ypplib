# Implementation Notes

## Testing

This library makes use of some [doctest][doctest] tests and has
a custom script for testing.

Originally I wanted to use the [unittest][unittest] unit
testing framework, but that was much more work than the
tests that I had already made from before.  So I wrote
a small script that is used to collect test output, and
run tests to make sure that there are no regressions
during subsequent runs.  This is all in the `tests`
folder.  Also, the `data` folder contains data that
was imported from a previous project.

In the tests folder there are a number of scripts and
test data:

- doctests.sh - Runs defined [doctest][doctest] tests
- test-ypp.py - Used to create test output and verify test cases
- gen-tests.sh - script used to generate test data.

The following files contain test data:

- `demokeys.tgz` : test credentials
- `z*.json`: individual test case files

  [doctest]: https://docs.python.org/3/library/doctest.html
  [unittest]: https://docs.python.org/3/library/unittest.html
