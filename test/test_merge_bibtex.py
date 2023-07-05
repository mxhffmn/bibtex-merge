import unittest

from pybtex.database.input import bibtex

from merge_bibtex import process_identical_keys, process_similar_keys, parse_bibtex_files


class MergeBibtexTest(unittest.TestCase):

    def test_processing_identical_keys(self):
        # load bib data
        bib_file_1, bib_file_2 = parse_bibtex_files('test/resources/testbib_1.bib', 'test/resources/testbib_2.bib',
                                                    'test/resources/testbib_output.bib', True)

        process_identical_keys(bib_file_1, bib_file_2, 'test/resources/testbib_output.bib', False, False)

        # load output bib
        bib_file_output = bibtex.Parser().parse_file('test/resources/testbib_output.bib')
        self.assertIsNotNone(bib_file_output)
        self.assertSetEqual({'jame76', 'colu92', 'gree00'}, set(bib_file_output.entries.keys()))

    def test_processing_very_similar_entries(self):
        # load bib data
        bib_file_1, bib_file_2 = parse_bibtex_files('test/resources/testbib_1.bib', 'test/resources/testbib_2.bib',
                                                    'test/resources/testbib_output.bib', True)

        process_similar_keys(bib_file_1, bib_file_2, 'test/resources/testbib_output.bib', False, False)

        # load output bib
        bib_file_output = bibtex.Parser().parse_file('test/resources/testbib_output.bib')
        self.assertIsNotNone(bib_file_output)
        self.assertSetEqual({'smit54', 'colu92', 'phil99', 'jame76', 'gree00'}, set(bib_file_output.entries.keys()))

        process_similar_keys(bib_file_1, bib_file_2, 'test/resources/testbib_output.bib', True, False)

        # load output bib
        bib_file_output = bibtex.Parser().parse_file('test/resources/testbib_output.bib')
        self.assertIsNotNone(bib_file_output)
        self.assertSetEqual({'smit55', 'colu92', 'phil98', 'jame76', 'gree00'}, set(bib_file_output.entries.keys()))

    def test_processing_without_overwrite(self):
        self.assertRaises(FileExistsError,
                          lambda: parse_bibtex_files('test/resources/testbib_1.bib', 'test/resources/testbib_2.bib',
                                                     'test/resources/testbib_output.bib', False))
