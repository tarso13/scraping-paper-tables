# scraping-paper-tables
Installation Guidelines:

Prior to running the application, it is essential to verify that Python and Elasticsearch are successfully installed. To streamline the initialization process, a “requirements.txt” file is provided within the repository. This file encompasses required packages that can automatically be installed by running “pip install -r requirements.txt”. This command should be run within the “scraping-paper-tables” repository. 

Firstly, the command that should be run is “python .\nasa_ads_journal_search.py” on Windows or “python ./nasa_ads_journal_search.py” on Linux  within the “scraping-paper-tables” directory. Once these steps are done, Elasticsearch needs to be initiated. This can be achieved by executing the following command: “.\bin\elasticsearch” on Windows or “./bin/elasticsearch” on Linux within the elasticsearch directory. 

To create the dataset and upload all tables to the elastic indexes, the command that should be run is “python .\extract_tables.py” on Windows or “python ./extract_tables.py” on Linux within the “table-extracts” directory present in “scraping-paper-tables” directory. The web application can be launched using the command: “python -m uvicorn api:app --reload” within the “fast-api” repository present in “scraping-paper-tables”. These instructions facilitate a streamlined setup, allowing for the successful deployment of the web application and interaction with the user interface (UI).

Execution/Logical Steps:
1) Query to ads:
	Initialize and open file to write the results
	Form query
    Encode query
	Parse results to get bibcodes (extract them in json format)
	For each result, extract bibcode
	For each bibcode:
		Form the url (including the format of the paper)
		Get url + identify falsy existence for journals
		Write url directly to file for download
2) Create primary index if it does not exist
   Create secondary index if it does not exist
3) Download publication:
   	Check domain + append to directory name
	Download html publication
	Extract doi and write to file
	Special case: A&A tables written to extra files in sub folder
4) Extract tables:
	Parse all entries in each directory created
	For each entry, check if it is already extracted (extracted entries are appended to a list files_extracted) and get content of file
	If it is an A&A original publication, store the metadata in a dictionary (k=doi, v=metadata)
	Extract tables with bs4 tag "table" and identify supplementary tables (by text)
	If tables found:
		A&A:
			Retrieve metadata from dictionary
			Get date
			Get footnotes
			Get table info
		IOPScience:
			Get metadata from journal
			Check for mrt tables:
				Download them
				Read the content and get line by line units, explanations, etc
				Ascii read table
				Convert to json 
				Adjust metadata from original publication (doi, table_id)
				Write to json file
		Get available doc index id (elastic index count + 1)
		For each table:
			Add retrieval date + paper access property to metadata 
			IOPScience:
				append table id to title
				Retrieve table info (caption, notes) (all at once -> identify by table id)
				Retrieve table footnotes (identify and split them - all sup tags)
			MNRAS:
				Extract "extra" metadata (usually stored in script tag in html) [publication_date, journal,authors, paper_title, doi]
				Add the rest of the metadata 
				Check for access property
				If extra metadata are not set correctly -> meta tags (like the other journals)
			Actual Extraction:
				IOPScience:
					Set journal to IOPscience
					Remove notes from metadata if empty
				Find colspan headers (one header, multiple columns), rowspan headers (one header, multiple rows) and unparsable (img) headers
				Adjust table headers and organize them as rows for the metadata 
				MNRAS:
					Find table id from html
					Add journal and title to metadata
					Add mnras table info and footnotes (from html)
				Set table id for all journals 
				If json file exists, set json data to null and do not proceed with the table extraction
				Find empty or unparsable (img) table cells (usually same cell content to 2 rows or no header)
				Convert table info to json
				Remove '.' from table cells
				Set empty data to null
				Add each table cell to a list
				Adjust table rows/cols in metadata if needed
				A&A:
				    Validate footnotes (because in previous step, sup tags are detected as footnotes - may contain numbers, letters, etc)
					Identify footnotes in data_found based on journal name
					Replace foonote in json_obj['content']
					Add header attribute (true-false)
					Add extra attribute 'note' with footnote value
					Convert all row to json 
					Write to json file 				
5) If json data:
	Check if doi exists in elastic index ("query": {"match_phrase": {"metadata.doi": doi}} - es.search(index=parent_index, body=query))
 	If doi exists: check documents for metadata["table_id"]. If table_id does not exist - > index document to parent index
				
UI Components:
1) Index page:
	 Multiple forms (one for each option) with custom buttons
		On submit -> redirect to query page
2) Query page:
	Form 1:
		One or two input fields based on the query
		Dropdown menu for journal searches
		MRT checkbox for doi searches 
		Search (submit) button -> redirects to results page*
	Form 2:
		Back (submit) button -> redirects to index page
3) Results page:
	Results container 
	Form with back (submit) button -> redirects to query page

*before redirecting, call the desired elasticsearch query function 