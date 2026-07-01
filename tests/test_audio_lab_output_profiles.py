"""Tests for DSPPage / Output Profiles — requires pytest-qt."""


def test_dsp_page_renders(qtbot):
    from ui.audio_lab.dsp_page import DSPPage
    page = DSPPage()
    qtbot.addWidget(page)
    page.show()
    assert page.isVisible()
    assert page.navigate_requested is not None


def test_dsp_page_upsampling_disabled(qtbot):
    from ui.audio_lab.dsp_page import DSPPage
    page = DSPPage()
    qtbot.addWidget(page)
    assert hasattr(page, '_upsample_enable')
    assert hasattr(page, '_upsample_rate')
    assert hasattr(page, '_room_enable')
    assert hasattr(page, '_room_file_btn')
