## Synopsis

This is a toy project, it indexes Gutenberg project using the standard tf-idf, and query using cosine-distance. The indexing files are less than 500 MBs compressed, 3GB uncompressed. This is a toy project of me for learning tf-idf, not production code in any level.

## Example
Run 'query_main.py' to query:

>:  Darcy
query 183 documents
	The Eyes Have It, by Gordon Randall Garrett 0.000454257793239 30833
	Pride and Predjudice, a play, by Mary Keith Medbery Mackaye 0.000339358663544 37431
	Pride and Prejudice, by Jane Austen 0.000217050008635 1342
	Parlous Times, by David Dwight Wells 0.000154920544249 34925
	The Knight Of Gwynne, Vol. II (of II), by Charles James Lever 0.000151109468194 35756
	Hope Mills, by Amanda M. Douglas 0.000146005289842 30436
	Why Joan?, by Eleanor Mercein Kelly 0.000135829768966 34801
	The Knight Of Gwynne, Vol. I (of II), by Charles James Lever 0.000116505169663 35755
	Georgina of the Rainbows, by Annie Fellows Johnston 0.000106133160749 39596
	Hugo, by Arnold Bennett 7.17375476464e-05 15712


## Motivation

I cam across the Gutenberg-tar project where all the files are in txt format, making it very easy to process. The size is adequately big for an information retrieval project. 

## Installation

If you want to try indexing yourself, download the text file from http://www.gutenberg-tar.com/. Extract them at any folder and assign 'target_path' (in indexer.py) accordingly.


## Contributors

Let people know how they can dive into the project, include important links to things like issue trackers, irc, twitter accounts if applicable.

## License

A short snippet describing the license (MIT, Apache, etc.)
