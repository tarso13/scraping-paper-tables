# scraping-paper-tables
Installation Guidelines:

Prior to running the application, it is essential to verify that Python and Elasticsearch are successfully installed. To streamline the initialization process, a “requirements.txt” file is provided within the repository. This file encompasses required packages that can automatically be installed by running “pip install -r requirements.txt”. This command should be run within the “scraping-paper-tables” repository. 

Firstly, the command that should be run is “python .\nasa_ads_journal_search.py” on Windows or “python ./nasa_ads_journal_search.py” on Linux  within the “scraping-paper-tables” directory. Once these steps are done, Elasticsearch needs to be initiated. This can be achieved by executing the following command: “.\bin\elasticsearch” on Windows or “./bin/elasticsearch” on Linux within the elasticsearch directory. 

To create the dataset and upload all tables to the elastic indexes, the command that should be run is “python .\extract_tables.py” on Windows or “python ./extract_tables.py” on Linux within the “table-extracts” directory present in “scraping-paper-tables” directory. The web application can be launched using the command: “python -m uvicorn api:app --reload” within the “fast-api” repository present in “scraping-paper-tables”. These instructions facilitate a streamlined setup, allowing for the successful deployment of the web application and interaction with the user interface (UI).

Execution/Logical Steps:

1. Query to ADS
    1. Initialize and open file to write the results 
    2. Form and encode query 
    4. Parse results to get bibcodes
    5. For each result, extract bibcode 
    6. For each bibcode:
        1. Form the url (including the format of the  paper to download)
        2. Get url and identify falsy existence for journals 
        3. Write url directly to file for download
2. Create primary and secondary elasticsearch indexes if they do not exist
3. Download publications (the steps below are per publication)
    1. Check domain and append it to directory name
    2. Download html publication 
    3. Extract DOI and write to file 
    4. Special case: A&A tables written to extra files in sub folder
4. Extract tables
    1. Parse all entries in each directory created 
    2. For each entry:
        1. Check if it is already extracted and get content of file
        2. If it is an A&A original publication, store the metadata in a dictionary (k=doi, v=meta-data) 
        3. Extract tables with tag "table" and identify supplementary tables (by text) 
        4. If tables found: 
            1. A&A: 
                1. Retrieve metadata from dictionary 
                2. Get date, footnotes, table info
            2. IOPScience: 
                1. Get metadata from journal 
                2. Check for mrt tables: 
                    1. Download them 
                    2. Read the content and get line by line units, explanations, etc 
                    3. Ascii read table 
                    4. Convert to json 
                    5. Adjust metadata from original publication (DOI, table_id) 
                    6. Write to json file 
            3. Get next available doc index id 
        3. For each table: 
            1. Add retrieval date and paper access property to metadata 
            2. IOPScience:
                1. Append table id to title 
                2. Retrieve table info (caption, notes) (all at once - identify by table id) 
            3. Retrieve table footnotes (identify and organize them)
            4. MNRAS: 
                1. Extract "extra" metadata (usually stored in script tag in html)
                2. Add the rest of the metadata 
                3. Check for access property 
                4. If extra metadata are not set correctly, extract them from meta tags (like the other journals) 
            5. Actual Extraction: 
                1. IOPScience: 
                    1. Set journal to IOPscience 
                    2. Remove notes from metadata if empty 
                2. Find colspan headers (one header, multiple columns), rowspan headers (one header, multiple rows) and unparsable (img) headers 
                3. Adjust table headers and organize them as rows for the metadata
                4. MNRAS: 
                    1. Find table id from html 
                    2. Add journal and title to metadata 
                    3. Add mnras table info and footnotes (from html)
                5. Set table id for all journals 
                6. If json file exists, set json data to null and do not proceed with the table extraction 
                7. For each row
                    1. Find empty or unparsable (img) table cells (usually same cell content to 2 rows or no header) 
                    2. Convert table info to json 
                    3. Remove '.' from table cells and set empty data to null 
                    5. Add each table cell to a list 
                    6. Adjust table rows/cols in metadata
                    7. Identify footnotes in data_found based on journal name 
                    8. Replace foonote in json_obj['content'] 
                    9. Add header attribute to table header cells
                    10. Add extra attribute 'note' with footnote value
                    11. Convert all row to json 
                    12. Write to json file
                19. Check if doi exists in elastic index
                20. If doi exists: check documents for the same table id
                21. If table id does not exist, index document to parent index
                22. Get next available doc index id for secondary index
                23. Repeat steps h-j to append mrt tables to index
				
UI Components:

1. Index page:
    1. Multiple forms with custom buttons - On click, they redirect to query page
2) Query page:
    1. Form 1:
	    1. One or two input fields based on the query
	    2. Dropdown menu for journal searches
	    3. MRT checkbox for DOI searches 
		4. Search button - On click, redirects to results page*
	2. Form 2:
	    1. Back button - On click, redirects to index page
3) Results page:
    1. Results container 
	2. Form with back button - redirects to query page
	
*before redirecting, call the desired elasticsearch query function 

