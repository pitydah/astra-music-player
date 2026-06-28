"""Tests for DFF/DSD file header parser.

Uses synthetic binary data — no real files needed.
"""
import struct
import tempfile
import os

import pytest

from audio.dff_parser import parse_dff, DffHeader


def _make_dff(sample_rate=2822400, channels=2, is_dst=False, data_size=4096):
    """Build a minimal valid DFF file in memory and return (bytes, expected_header)."""
    fmt = b"DST " if is_dst else b"DSD "
    comp = b"DST " if is_dst else b"DSD "

    # PROP chunk
    fs_chunk = b"FS  " + struct.pack(">Q", 4) + struct.pack(">I", sample_rate)
    chnl_chunk = b"CHNL" + struct.pack(">Q", 2) + struct.pack(">H", channels)
    cmpr_chunk = b"CMPR" + struct.pack(">Q", 4) + comp
    prop_data = fs_chunk + chnl_chunk + cmpr_chunk
    prop_chunk = b"PROP" + struct.pack(">Q", len(prop_data)) + prop_data

    # DSD chunk
    dsd_data = b"\x00" * data_size
    dsd_chunk = b"DSD " + struct.pack(">Q", len(dsd_data)) + dsd_data

    chunks = prop_chunk + dsd_chunk
    form_size = 4 + len(chunks)
    form = b"FRM8" + struct.pack(">Q", form_size) + fmt + chunks

    expected = DffHeader(
        sample_rate=sample_rate,
        channels=channels,
        data_offset=4 + 8 + 4 + len(prop_chunk),  # skip FRM8 + size + form type + PROP
        data_size=data_size,
        is_dst=is_dst,
    )
    return form, expected


class TestParseDff:
    def test_basic_dsf64_stereo(self):
        data, expected = _make_dff(2822400, 2)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dff") as f:
            f.write(data)
            tmp = f.name
        try:
            hdr = parse_dff(tmp)
            assert hdr.sample_rate == expected.sample_rate
            assert hdr.channels == expected.channels
            assert hdr.data_size == expected.data_size
            assert hdr.data_offset > 0
            assert hdr.is_dst is False
        finally:
            os.unlink(tmp)

    def test_dsd128(self):
        data, expected = _make_dff(5644800, 2)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dff") as f:
            f.write(data)
            tmp = f.name
        try:
            hdr = parse_dff(tmp)
            assert hdr.sample_rate == 5644800
        finally:
            os.unlink(tmp)

    def test_multichannel_5_1(self):
        data, expected = _make_dff(2822400, 6)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dff") as f:
            f.write(data)
            tmp = f.name
        try:
            hdr = parse_dff(tmp)
            assert hdr.channels == 6
        finally:
            os.unlink(tmp)

    def test_dst_compressed(self):
        data, expected = _make_dff(2822400, 2, is_dst=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dff") as f:
            f.write(data)
            tmp = f.name
        try:
            hdr = parse_dff(tmp)
            assert hdr.is_dst is True
        finally:
            os.unlink(tmp)

    def test_large_data_size(self):
        data, expected = _make_dff(2822400, 2, data_size=65536)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dff") as f:
            f.write(data)
            tmp = f.name
        try:
            hdr = parse_dff(tmp)
            assert hdr.data_size == 65536
        finally:
            os.unlink(tmp)

    def test_not_a_dff_file(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dff") as f:
            f.write(b"NOTA" + b"\x00" * 20)
            tmp = f.name
        try:
            with pytest.raises(ValueError, match="Not a valid DFF file"):
                parse_dff(tmp)
        finally:
            os.unlink(tmp)

    def test_not_dsd_form_type(self):
        bad = b"FRM8" + struct.pack(">Q", 8) + b"XXXX"
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dff") as f:
            f.write(bad)
            tmp = f.name
        try:
            with pytest.raises(ValueError, match="Not a DSD DFF file"):
                parse_dff(tmp)
        finally:
            os.unlink(tmp)

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dff") as f:
            tmp = f.name
        try:
            with pytest.raises((ValueError, struct.error, OSError)):
                parse_dff(tmp)
        finally:
            os.unlink(tmp)

    def test_file_too_short_for_header(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dff") as f:
            f.write(b"FRM8")
            tmp = f.name
        try:
            with pytest.raises((ValueError, struct.error)):
                parse_dff(tmp)
        finally:
            os.unlink(tmp)

    def test_missing_properties(self):
        data = b"FRM8" + struct.pack(">Q", 12) + b"DSD " + b"DSD " + struct.pack(">Q", 4) + b"\x00" * 4
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dff") as f:
            f.write(data)
            tmp = f.name
        try:
            with pytest.raises(ValueError, match="Could not read DFF properties"):
                parse_dff(tmp)
        finally:
            os.unlink(tmp)

    def test_dff_header_repr(self):
        hdr = DffHeader(2822400, 2, 100, 4096, False)
        assert hdr.sample_rate == 2822400
        assert hdr.channels == 2
        assert hdr.data_offset == 100
        assert hdr.data_size == 4096
        assert hdr.is_dst is False


class TestDffHeader:
    def test_immutable_like(self):
        hdr = DffHeader(2822400, 2, 100, 4096, False)
        assert hdr.sample_rate == 2822400
        assert hdr.channels == 2
        assert hdr.data_offset == 100
        assert hdr.data_size == 4096
        assert hdr.is_dst is False

    def test_dst_true(self):
        hdr = DffHeader(2822400, 2, 100, 4096, True)
        assert hdr.is_dst is True

    def test_zero_values(self):
        hdr = DffHeader(0, 0, 0, 0, False)
        assert hdr.sample_rate == 0
        assert hdr.channels == 0


class TestRealWorldEdgeCases:
    def test_prop_before_dsd_order(self):
        data, expected = _make_dff(2822400, 2)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dff") as f:
            f.write(data)
            tmp = f.name
        try:
            hdr = parse_dff(tmp)
            assert hdr.data_offset > 0
            assert hdr.data_size > 0
        finally:
            os.unlink(tmp)

    def test_nonzero_padding_after_prop(self):
        header_part, _ = _make_dff(2822400, 2, data_size=128)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dff") as f:
            f.write(header_part)
            tmp = f.name
        try:
            hdr = parse_dff(tmp)
            assert hdr.sample_rate == 2822400
            assert hdr.channels == 2
        finally:
            os.unlink(tmp)
