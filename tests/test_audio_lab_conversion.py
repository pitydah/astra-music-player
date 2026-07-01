"""Tests for ConversionPage — requires pytest-qt."""


def test_conversion_page_renders(qtbot):
    from ui.audio_lab.conversion_page import ConversionPage
    page = ConversionPage()
    qtbot.addWidget(page)
    page.show()
    assert page.isVisible()


def test_conversion_page_accepts_encoder(qtbot):
    from ui.audio_lab.conversion_page import ConversionPage
    encoder = object()
    page = ConversionPage(encoder=encoder)
    qtbot.addWidget(page)
    assert page._encoder is encoder


def test_conversion_empty_no_crash(qtbot):
    from ui.audio_lab.conversion_page import ConversionPage
    page = ConversionPage()
    qtbot.addWidget(page)
    page._start_conversion()
    assert page._status_label.text() == "Selecciona archivos primero."
