"""
    test windows
"""
import pytest

from IPTables_Guide.view.help_window import HelpWindow, display_help


def test_help_window(qtbot):
    """
        test HelpWindow
    """
    _ = qtbot

    # check if HelpWindow is created as a singleton
    assert HelpWindow._instance is None  # pylint: disable=W0212
    display_help()
    assert HelpWindow._instance is not None  # pylint: disable=W0212
    with pytest.raises(AssertionError):
        HelpWindow()
    h_w = HelpWindow.get_instance()
    display_help()
    assert HelpWindow._instance is not None  # pylint: disable=W0212
    assert h_w == HelpWindow.get_instance()
    assert HelpWindow.get_instance() == HelpWindow.get_instance()
    with qtbot.waitSignal(
        HelpWindow.get_instance().destroyed, timeout=100  # type: ignore
    ) as blocker:
        blocker.connect(HelpWindow.get_instance().destroyed)  # type: ignore
        HelpWindow.delete_instance()
    assert HelpWindow._instance is None  # pylint: disable=W0212
    with pytest.raises(RuntimeError):
        # h_w is already deleted
        print(h_w)
