from parse_html import * 

# Links to extract data from 
urls = [
    # 'https://iopscience.iop.org/article/10.1086/313034/fulltext/35878.text.html',
    'https://www.aanda.org/articles/aa/full_html/2018/08/aa32766-18/aa32766-18.html',
    'https://www.aanda.org/articles/aa/full_html/2023/06/aa44220-22/aa44220-22.html', 
    'https://www.aanda.org/articles/aa/full_html/2023/06/aa44161-22/aa44161-22.html',
    'https://www.aanda.org/articles/aa/full_html/2016/02/aa27620-15/aa27620-15.html',
    'https://www.aanda.org/articles/aa/full_html/2016/01/aa26356-15/aa26356-15.html'
]

# Main function to download initial urls and extract data
def main():
    print('Start downloading process...')
    download_all_html_files('publications', urls)
    print('Start extracting process...')
    extract_tables('publications')
    extract_tables('publications_aanda')
    extract_tables('publications_aanda/publications_aanda_tables')
    
main()