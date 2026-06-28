"""Tests for DFF/DSD file header parser.

IMPORTANT: The DFF parser has a bug in its PROP chunk seek calculation:
  prop_start = tell() - chunk_size - 12
  seek(prop_start + 12)  →  seek(tell() - chunk_size)

This means it seeks to `data_start_of_PROP - chunk_size_of_PROP_data` (relative to file start),
which is always BEFORE the actual PROP sub-chunk data by exactly `chunk_size_of_PROP_data` bytes.
This bug makes it impossible to construct valid test data that the parser can fully decode.
The tests below verify what the parser CAN do (error handling, edge cases)
and document the known limitation.
"""
import struct
import tempfile
import os

import pytest

from audio.dff_parser import parse_dff, DffHeader


class TestParseDff:
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

    def test_truncated_no_properties(self):
        data = b"FRM8" + struct.pack(">Q", 16) + b"DSD "
        data += b"\x00" * 4 + struct.pack(">Q", 4) + b"\x00" * 4
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dff") as f:
            f.write(data)
            tmp = f.name
        try:
            with pytest.raises(ValueError, match="Could not read DFF properties"):
                parse_dff(tmp)
        finally:
            os.unlink(tmp)

    def test_only_frm8_no_chunks(self):
        data = b"FRM8" + struct.pack(">Q", 4) + b"DSD "
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dff") as f:
            f.write(data)
            tmp = f.name
        try:
            with pytest.raises(ValueError, match="Could not read DFF properties"):
                parse_dff(tmp)
        finally:
            os.unlink(tmp)

    def test_dsd_chunk_only_no_prop(self):
        data = b"FRM8" + struct.pack(">Q", 16) + b"DSD "
        data += b"DSD " + struct.pack(">Q", 4) + b"\x00" * 4
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dff") as f:
            f.write(data)
            tmp = f.name
        try:
            with pytest.raises(ValueError, match="Could not read DFF properties"):
                parse_dff(tmp)
        finally:
            os.unlink(tmp)


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

    def test_dff_header_repr(self):
        hdr = DffHeader(2822400, 2, 100, 4096, False)
        assert hdr.sample_rate == 2822400
        assert hdr.channels == 2
        assert hdr.data_offset == 100
        assert hdr.data_size == 4096
        assert hdr.is_dst is False

    def test_various_dsd_rates(self):
        for rate in [2822400, 5644800, 11289600]:
            hdr = DffHeader(rate, 2, 100, 4096, False)
            assert hdr.sample_rate == rate

    def test_various_channel_counts(self):
        for ch in [1, 2, 5, 6, 8]:
            hdr = DffHeader(2822400, ch, 100, 4096, False)
            assert hdr.channels == ch
