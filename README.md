# EES-Res
Resources for Semitic languages of Ethiopia and Eritrea.

## Treebanks

Files in CoNLL-U format are in the `conllu` folder. They have the extension `.conllu`.

CoNNL-U files may be "empty", with only the 'ID' and 'FORM' fields filled out.
These can be edited with Conllu Editor.

They may also be "morphology only", with 'ID', 'FORM', 'LEMMA', 'UPOS', and 'FEATS' fields filled out.
These can be edited with any of the annotation tools.

"Complete" CoNNL-U files include at least 'ID', 'FORM', 'LEMMA', 'UPOS', 'FEATS', 'HEAD', and 'DEPREL' fields filled out.

## Raw Data

Files with raw data are in the `text` folder. They have the extension `.txt`.

They consist of lines with tokenized sentences and possibly also commented lines containing sentence IDs. For example,

	# am1
	አበበ በሶ በላ ።
	
Segmented words are indicated as follows:

	አስተማሪያችን = (አስተርማሪ ኣችን) በሶ ትበላለቸ = (ት በላ ኣለች) ።
	
Raw data files can be converted to empty CoNNL-U files using `datafile2conllu()`, found in `src/utils.py`.

	>>> import utils
	>>> utils.datafile2conllu("../text/amh/am_test1.txt", "../conllu/amh/am_test1.conllu")