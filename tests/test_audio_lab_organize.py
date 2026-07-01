"""Tests for OrganizePage — requires pytest-qt."""


def test_organize_page_renders(qtbot):
    from ui.audio_lab.organize_page import OrganizePage
    page = OrganizePage(db=None)
    qtbot.addWidget(page)
    page.show()
    assert page.isVisible()


def test_organize_no_files_no_preview(qtbot):
    from ui.audio_lab.organize_page import OrganizePage
    page = OrganizePage(db=None)
    qtbot.addWidget(page)
    page._generate_preview()
    assert page._status_label.text() == "Selecciona una carpeta primero."


def test_organize_apply_without_preview_does_nothing(qtbot):
    from ui.audio_lab.organize_page import OrganizePage
    page = OrganizePage(db=None)
    qtbot.addWidget(page)
    page._apply_changes()
    assert not page._files
