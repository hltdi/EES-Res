# EES-Res
Resources for Semitic languages of Ethiopia and Eritrea.

## Treebanks

Files in CoNLL-U format are in the `conllu` folder. They have the extension `.conllu`.

CoNNL-U files may be "empty", with only the 

They may also be "morphology only", containing UPOS, XPOS, and feats.

"Complete" CoNNL-U files contain 

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