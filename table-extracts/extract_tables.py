from download_html import download_all_html_files
from parse_html import extract_downloaded_tables
# Links to extract data from 
urls = [
    'https://www.aanda.org/articles/aa/full_html/2018/08/aa32766-18/aa32766-18.html',
    'https://www.aanda.org/articles/aa/full_html/2023/06/aa44220-22/aa44220-22.html', 
    'https://www.aanda.org/articles/aa/full_html/2023/06/aa44161-22/aa44161-22.html',
    'https://www.aanda.org/articles/aa/full_html/2016/02/aa27620-15/aa27620-15.html',
    'https://www.aanda.org/articles/aa/full_html/2016/01/aa26356-15/aa26356-15.html',
    'https://iopscience.iop.org/article/10.3847/1538-4357/acd250',
    'https://iopscience.iop.org/article/10.3847/1538-3881/acdd6f'
]

# Main function to download initial urls and extract data
def main():
    download_extra_files = False
    print('Start downloading process...')
    download_all_html_files('publications', urls, download_extra_files)
    print('Start extracting process...')
    extract_downloaded_tables('publications_aanda')
    extract_downloaded_tables('publications_aanda/publications_aanda_tables')
    extract_downloaded_tables('publications_iopscience')
    
main()