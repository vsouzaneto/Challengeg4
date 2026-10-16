"""Intervalos de bytes do vídeo tutorial (o player só avança e volta com respostas 206)."""

from unittest import TestCase

from server import byte_range


class ByteRangeTests(TestCase):
    def test_open_and_closed_ranges(self):
        self.assertEqual(byte_range("bytes=0-", 1000), (0, 999))
        self.assertEqual(byte_range("bytes=100-199", 1000), (100, 199))
        self.assertEqual(byte_range("bytes=900-5000", 1000), (900, 999))

    def test_suffix_range_returns_last_bytes(self):
        self.assertEqual(byte_range("bytes=-200", 1000), (800, 999))
        self.assertEqual(byte_range("bytes=-5000", 1000), (0, 999))

    def test_invalid_or_unsatisfiable(self):
        for header in (None, "", "bytes=-", "items=0-10", "bytes=0-1,5-9", "bytes=2000-"):
            self.assertIsNone(byte_range(header, 1000), header)
