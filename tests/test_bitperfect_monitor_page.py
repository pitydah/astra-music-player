"""Tests for BitperfectMonitorPage UI — requires qtbot."""


def test_bitperfect_monitor_renders(qtbot):
    from ui.audio_lab.bitperfect_monitor_page import BitperfectMonitorPage
    page = BitperfectMonitorPage()
    qtbot.addWidget(page)
    page.show()
    assert page.isVisible()
    assert page.navigate_requested is not None


def test_update_from_verified_report(qtbot):
    from ui.audio_lab.bitperfect_monitor_page import BitperfectMonitorPage
    from audio.diagnostics.bitperfect_report import BitperfectReport
    page = BitperfectMonitorPage()
    qtbot.addWidget(page)
    report = BitperfectReport(
        status="verified", verified=True,
        input_sample_rate=44100, input_bit_depth=16, input_channels=2,
        output_sample_rate=44100, output_format="S16_LE",
        device="hw:0,0")
    page.update_from_report(report)
    assert "Verificado" in page._status_label.text()


def test_update_from_broken_report(qtbot):
    from ui.audio_lab.bitperfect_monitor_page import BitperfectMonitorPage
    from audio.diagnostics.bitperfect_report import BitperfectReport
    page = BitperfectMonitorPage()
    qtbot.addWidget(page)
    report = BitperfectReport(
        status="broken",
        reasons=["EQ activo", "Resampling activo"],
        input_sample_rate=44100)
    page.update_from_report(report)
    assert page._warnings_list.text() != ""
