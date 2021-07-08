The folder __1_external__ contains external data, which is used for building the dataset. This entails:

- Data from the  EIOPA register for European insurance companies and the accompanying GLEIF identifier data. This data is already in RDF format and is used to build the underlying graph
- Templates containing natural language questions and SPARQL queries with a placeholder. This placeholder is to be filled using the generator query. There are several files for training, validation and testing. Test templates are in a folder to enable faster generation further on in the process.

__2_interim__ contains raw natural language-query pairs, where the placeholder is already filled in.

__3_processed__ contains the ready-to-use language pairs. These are already byte-pair encoded.

__4_vocabularies__ contains some "helper" files from the preprocessing like the vocabularies and the byte-pair 
encodings.

__5_model_input__ is used to make the repo more light and is the next to 1_external the only one synced to the repo. It contains the files needed to train the network und build the binarized fairseq dataset. You can copy the files and adapt the names here manually or use a script from the script folder for this.
