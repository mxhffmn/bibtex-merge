import argparse
import os
import string
from typing import List, Tuple

import nltk
from Levenshtein import ratio, seqratio
from nltk.corpus import stopwords
from pybtex.database import BibliographyData
from pybtex.database.input import bibtex
from sklearn.feature_extraction.text import TfidfVectorizer


def parse_args() -> argparse.Namespace:
    """
    Parses the arguments that were given via the command line.
    :return: the parsed arguments
    """

    parser = argparse.ArgumentParser(
        description='Merges two existing bibtex files (.bib) into a single file. '
                    'Thereby, not only identical entries or keys are merged but also similar ones. '
                    'The behavior of the tool can be customized by multiple parameters.')
    parser.add_argument(dest='bib_file_1', type=str,
                        help='the path to the first bibtex file. Can be absolute or relative.')
    parser.add_argument(dest='bib_file_2', type=str,
                        help='the path to the second bibtex file. Can be absolute or relative.')
    parser.add_argument('--output', dest='output', type=str, default='merged.bib',
                        help='the name of the merged output file.')
    parser.add_argument('--overwrite', dest='overwrite', action='store_true',
                        help='if set, an existing output file is overwritten.')
    parser.add_argument('--prefer_second', dest='prefer_second', action='store_true',
                        help='if set, the entry in the second file will be preferred in case of similarity. '
                             'By default, the entry of the first file will be preferred.')
    parser.add_argument('--only_identical', dest='only_identical', action='store_true',
                        help='if set, only identical entries will be merged (without the use of similarity). '
                             'An entry is identical if the keys are identical or if all other fields are identical.')
    parser.add_argument('--dry_run', dest='dry_run', action='store_true',
                        help='if set, the tool will perform a dry-run, only printing its actions '
                             'without actually performing them. This is useful for testing and debugging.')
    return parser.parse_args()


def parse_bibtex_files(path_bib_1: str, path_bib_2: str, path_output: str, overwrite: bool) \
        -> Tuple[BibliographyData, BibliographyData]:
    """
    Parses the two bibtex files that are given as parameters.
    Additionally, the parameters are checked w.r.t. their validity.
    :param path_bib_1: path to the first bibtex file
    :param path_bib_2: path to the second bibtex file
    :param path_output: path to the output file
    :param overwrite: whether to overwrite the output file
    :return: a pair of the two parsed bibtex files
    """

    # check if both files exist at specified path and if output file does not exist
    if not os.path.exists(path_bib_1):
        raise FileNotFoundError(f'Specified path of bib file 1 (\'{path_bib_1}\') does not exist.')
    if not os.path.exists(path_bib_2):
        raise FileNotFoundError(f'Specified path of bib file 2 (\'{path_bib_2}\') does not exist.')
    if os.path.exists(path_output) and not overwrite:
        raise FileExistsError(f'Specified output path (\'{path_output}\') does already exist.')
    # load both bib files
    bib_file_1 = bibtex.Parser(encoding='utf-8').parse_file(path_bib_1)
    bib_file_2 = bibtex.Parser(encoding='utf-8').parse_file(path_bib_2)
    if bib_file_1 is not None and bib_file_2 is not None:
        print('Successfully loaded both bibtex files. Starting analysis.')

    return bib_file_1, bib_file_2


def serialize_bibtex_entries(merged_keys: List[Tuple[str, str]], b_file_1: BibliographyData,
                             b_file_2: BibliographyData, path_output: str, prefer_second: bool, dry_run: bool):
    """
    Serializes the bibtex entries that are given in the form of key pairs.
    Depending on the parameters, a bibtex file is created which some of the entries are written to.
    :param merged_keys: a list of pairs of bibtex entry keys
    :param b_file_1: the first parsed bibtex file
    :param b_file_2: the second parsed bibtex file
    :param path_output: the path to the output file
    :param prefer_second: whether the entry from the first or the second file should be exported
    :param dry_run: whether to perform a dry run, i.e., write nothing into files, only print
    """

    if not dry_run:
        f = open(path_output, 'w', encoding='utf-8')
        f.write('%%%%%%%%%%%%%%%%%%%%%%%\n')
        f.write('%%% GENERATED BY MH %%%\n')
        f.write('%%%%%%%%%%%%%%%%%%%%%%%\n')
        f.write('\n')

    for i, (key_1, key_2) in enumerate(merged_keys):
        if prefer_second:
            entry_to_serialize = b_file_2.entries[key_2]
            comment_entry = b_file_1.entries[key_1]
            print(f'Key \'{key_2}\': Writing entry from bibtex file 2 and comment for bibtex file 1.')
        else:
            entry_to_serialize = b_file_1.entries[key_1]
            comment_entry = b_file_2.entries[key_2]
            print(f'Key \'{key_1}\': Writing entry from bibtex file 1 and comment from bibtex file 2.')

        # serialize
        if not dry_run:
            f.write(f'%%% START GROUP {i} %%%\n\n')
            f.write(entry_to_serialize.to_string('bibtex'))
            f.write('\n')
            ser_comm_entry: str = comment_entry.to_string('bibtex')
            ser_comm_entry = ser_comm_entry[1:]  # alter original type to avoid problems with some parsers
            ser_comm_entry = '%' + ser_comm_entry.strip().replace('\n', '\n%') + '\n\n'  # add every line as comment
            f.write(ser_comm_entry)
            f.write(f'%%% END GROUP {i} %%%\n\n')

    if not dry_run:
        f.close()


def process_identical_keys(b_file_1: BibliographyData, b_file_2: BibliographyData, path_output: str,
                           prefer_second: bool, dry_run: bool):
    """
    Processes the case where only identical keys should be matched.
    :param b_file_1: the first parsed bibtex file
    :param b_file_2: the second parsed bibtex file
    :param path_output: the path to the output file
    :param prefer_second: whether the entry from the first or the second file should be exported
    :param dry_run: whether to perform a dry run, i.e., write nothing into files, only print
    """

    print('I am looking for entries with identical keys.')
    merged_list_of_keys = set(b_file_1.entries.keys()).intersection(set(b_file_2.entries.keys()))
    if len(merged_list_of_keys) > 0:
        print('Found the following identical keys:')
        for key in merged_list_of_keys:
            print(key)

        # serialize entries
        serialize_bibtex_entries([(entry, entry) for entry in merged_list_of_keys], b_file_1, b_file_2, path_output,
                                 prefer_second, dry_run)
    else:
        print('Found no identical keys.')


def cleanup_text(text: str) -> str:
    """
    Cleans up the given text by removing line breaks, punctuation, and stopwords.
    :param text: the text to clean up
    :return: the text after cleaning up
    """

    # cleanup
    new_text = text.replace('\n', ' ').replace('\r', ' ').replace('\'', '')

    # remove punctuation
    new_text = ''.join([c for c in new_text if c not in string.punctuation])

    # remove stopwords
    new_text = ' '.join([w for w in new_text.split() if w.lower() not in list(stopwords.words('english'))])

    return new_text.lower()


def process_similar_keys(b_file_1: BibliographyData, b_file_2: BibliographyData, path_output: str, prefer_second: bool,
                         dry_run: bool):
    """
    Processes the case where similar entries should be matched.
    :param b_file_1: the first parsed bibtex file
    :param b_file_2: the second parsed bibtex file
    :param path_output: the path to the output file
    :param prefer_second: whether the entry from the first or the second file should be exported
    :param dry_run: whether to perform a dry run, i.e., write nothing into files, only print
    """

    print('I am looking for similar entries.')

    b_keys_1 = list(b_file_1.entries.keys())
    b_keys_2 = list(b_file_2.entries.keys())

    # compare title with Levenshtein similarity
    title_sims = {}
    for k1 in b_keys_1:
        title_1 = b_file_1.entries[k1].fields['title']
        for k2 in b_keys_2:
            title_2 = b_file_2.entries[k2].fields['title']
            title_sims[(k1, k2)] = ratio(cleanup_text(title_1), cleanup_text(title_2))

    # compare authors with sequence similarity
    def get_last_names(entry) -> List[str]:
        authors = entry.persons['author']
        last_names = []
        for a1 in authors:
            last_names.extend(a1.last_names)
        return last_names

    author_sims = {}
    for k1 in b_keys_1:
        last_names_1 = get_last_names(b_file_1.entries[k1])
        for k2 in b_keys_2:
            last_names_2 = get_last_names(b_file_2.entries[k2])
            author_sims[(k1, k2)] = seqratio(last_names_1, last_names_2)

    # compare all other fields as a bag of words
    def get_all_fields(entry) -> str:
        texts = ''
        for key in list(entry.fields.keys()):
            texts = texts + entry.fields[key] + ' '
        return texts[:-1]

    bow_sims = {}
    vectorizer = TfidfVectorizer(stop_words='english')
    for k1 in b_keys_1:
        text_k1 = get_all_fields(b_file_1.entries[k1])
        for k2 in b_keys_2:
            text_k2 = get_all_fields(b_file_2.entries[k2])
            tfidf = vectorizer.fit_transform([text_k1, text_k2])
            bow_sims[(k1, k2)] = (tfidf * tfidf.T).A[0, 1]

    # aggregate similarities
    agg_sims = {}
    for k1 in b_keys_1:
        for k2 in b_keys_2:
            agg_sims[(k1, k2)] = 0.375 * title_sims[(k1, k2)] \
                                 + 0.375 * author_sims[(k1, k2)] \
                                 + 0.25 * bow_sims[(k1, k2)]

    # delete all entries below a certain threshold
    for key in list(agg_sims):
        if agg_sims[key] < 0.7:
            del agg_sims[key]

    # select the best matches for each entry
    matches = []
    for k1 in b_keys_1:
        entries = []
        for k2 in b_keys_2:
            if (k1, k2) in agg_sims:
                entries.append((k1, k2, agg_sims[(k1, k2)]))
        if len(entries) > 0:
            entries.sort(key=lambda a: a[2], reverse=True)  # sort for highest similarity in front
            matches.append((entries[0][0], entries[0][1]))
            for e in entries:
                del agg_sims[(e[0], e[1])]

    serialize_bibtex_entries(matches, b_file_1, b_file_2, path_output, prefer_second, dry_run)


def merge_bibtex():
    """
    Main method that is called when the script is executed.
    """

    args = parse_args()

    if args.dry_run:
        print('Starting dry-run: no files will be created/no actions performed!')

    bib_file_1, bib_file_2 = parse_bibtex_files(args.bib_file_1, args.bib_file_2, args.output, args.overwrite)

    if args.only_identical:
        process_identical_keys(bib_file_1, bib_file_2, args.output, args.prefer_second, args.dry_run)
    else:
        nltk.download('stopwords')
        process_similar_keys(bib_file_1, bib_file_2, args.output, args.prefer_second, args.dry_run)


if __name__ == "__main__":
    merge_bibtex()
