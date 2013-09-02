# coding: utf-8

from termcolor import colored


def pytest_report_teststatus(report):
    if report.when != "call":
        return None, None, None
    if report.passed:
        letter = colored('✓', 'green')
    elif report.skipped:
        if hasattr(report, 'wasxfail'):
            letter = colored('✗', 'blue')
        else:
            letter = colored('s', 'blue')
    elif report.failed:
        letter = colored('✗', 'red')
    return report.outcome, letter, report.outcome.upper()
