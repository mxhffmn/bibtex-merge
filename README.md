merge_bibtex.py
=======

## Description

Merges two existing bibtex files (.bib) into a single file. Thereby, not only identical entries or keys are merged but
also similar ones. The behavior of the tool can be customized by multiple parameters.

## Usage:

```bash
python3 merge_bibtex.py [-h] [--output OUTPUT] [--overwrite] [--prefer_second] [--only_identical] [--dry_run] bib_file_1 bib_file_2
```

## Required Positional Parameters

| parameter    | description                                                      |
|:-------------|:-----------------------------------------------------------------|
| `bib_file_1` | the path to the first bibtex file. Can be absolute or relative.  |
| `bib_file_2` | the path to the second bibtex file. Can be absolute or relative. |

## Optional Parameters

| parameter          | description                                                                                                                                                          |
|:-------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--output OUTPUT`  | the name of the merged output file.                                                                                                                                  |
| `--overwrite`      | if set, an existing output file is overwritten.                                                                                                                      |
| `--prefer_second`  | if set, the entry in the second file will be preferred in case of similarity. By default, the entry of the first file will be preferred.                             |
| `--only_identical` | if set, only identical entries will be merged (without the use of similarity). An entry is identical if the keys are identical or if all other fields are identical. |
| `--dry_run`        | if set, the tool will perform a dry-run, only printing its actions without actually performing them. This is useful for testing and debugging.                       |

## License

MIT
