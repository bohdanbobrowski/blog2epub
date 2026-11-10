import unittest

from blog2epub.blog2epub_cli import create_parser, valid_quality


class TestCliQuality(unittest.TestCase):
    def test_valid_quality_values(self):
        self.assertEqual(valid_quality("1"), 1)
        self.assertEqual(valid_quality("40"), 40)
        self.assertEqual(valid_quality("100"), 100)

    def test_out_of_range_quality_rejected(self):
        import argparse

        for bad in ("0", "-5", "101", "999"):
            with self.assertRaises(argparse.ArgumentTypeError):
                valid_quality(bad)

    def test_parser_rejects_out_of_range_quality(self):
        parser = create_parser()
        with self.assertRaises(SystemExit) as ctx:
            parser.parse_args(["http://example.com", "--quality", "999"])
        self.assertEqual(ctx.exception.code, 2)
        args = parser.parse_args(["http://example.com", "--quality", "75"])
        self.assertEqual(args.quality, 75)
        self.assertEqual(parser.parse_args(["http://example.com"]).quality, 40)


if __name__ == "__main__":
    unittest.main()
