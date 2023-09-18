from download_html import download_all_html_files
from parse_html import extract_downloaded_tables

aanda_urls = [
    'https://www.aanda.org/articles/aa/full_html/2010/16/aa15738-10/aa15738-10.html',
    'https://www.aanda.org/articles/aa/full_html/2011/12/aa18034-11/aa18034-11.html',
    'https://www.aanda.org/articles/aa/full_html/2012/12/aa20527-12/aa20527-12.html',
    'https://www.aanda.org/articles/aa/full_html/2013/12/aa22728-13/aa22728-13.html',
    'https://www.aanda.org/articles/aa/full_html/2014/12/aa24852-14/aa24852-14.html',
    'https://www.aanda.org/articles/aa/full_html/2015/12/aa27634-15/aa27634-15.html',
    'https://www.aanda.org/articles/aa/full_html/2016/12/aa29262-16/aa29262-16.html',
    'https://www.aanda.org/articles/aa/full_html/2017/12/aa31472-17/aa31472-17.html',
    'https://www.aanda.org/articles/aa/full_html/2018/12/aa33442-18/aa33442-18.html',
    'https://www.aanda.org/articles/aa/full_html/2019/12/aa36750-19/aa36750-19.html',
    'https://www.aanda.org/articles/aa/full_html/2020/12/aa39232-20/aa39232-20.html',
    'https://www.aanda.org/articles/aa/full_html/2021/12/aa41506-21/aa41506-21.html',
    'https://www.aanda.org/articles/aa/full_html/2022/12/aa45084-22/aa45084-22.html',
    'https://www.aanda.org/articles/aa/full_html/2023/09/aa46128-23/aa46128-23.html'
]

# https://academic.oup.com/mnras/article/409/4/1705/986372 references
mnras_urls = [
    'https://academic.oup.com/mnras/article/409/4/1705/986372', 
    'https://academic.oup.com/mnras/article/418/4/2816/1030300',
    'https://academic.oup.com/mnras/article/427/4/3396/973924',
    'https://academic.oup.com/mnras/article/436/4/3856/989398',
    'https://academic.oup.com/mnras/article/445/4/4504/1754031',
    'https://academic.oup.com/mnras/article/454/4/4484/1001540',
    'https://academic.oup.com/mnras/article/463/4/4533/2646540',
    'https://academic.oup.com/mnras/article/472/4/5023/4083624',
    'https://academic.oup.com/mnras/article/481/4/5687/5116176',
    'https://academic.oup.com/mnras/article/490/4/5931/5588612',
    'https://academic.oup.com/mnrasl/article/499/1/L121/5908386?login=true',
    'https://academic.oup.com/mnras/article/508/4/6013/6395325',
    'https://academic.oup.com/mnras/article/517/4/6205/6772454',
    'https://academic.oup.com/mnrasl/article/526/1/L41/7028781'
]

# Links to extract data from 
urls = [
    'https://www.aanda.org/articles/aa/full_html/2018/08/aa32766-18/aa32766-18.html',
    'https://www.aanda.org/articles/aa/full_html/2023/06/aa44220-22/aa44220-22.html', 
    'https://www.aanda.org/articles/aa/full_html/2023/06/aa44161-22/aa44161-22.html',
    'https://www.aanda.org/articles/aa/full_html/2016/02/aa27620-15/aa27620-15.html',
    'https://www.aanda.org/articles/aa/full_html/2016/01/aa26356-15/aa26356-15.html',
    'https://iopscience.iop.org/article/10.3847/1538-4357/acd250',
    'https://iopscience.iop.org/article/10.3847/1538-3881/acdd6f',
    'https://academic.oup.com/mnras/article/524/4/5042/7227359', 
    'https://academic.oup.com/mnras/article/524/4/5060/7226714'
]

# Main function to download initial urls and extract data
def main():
    download_extra_files = True
    download_all_html_files('publications', aanda_urls, download_extra_files)
    download_all_html_files('publications', mnras_urls, download_extra_files)
    print('Start extracting process...')
    extract_downloaded_tables('publications_mnras')
    extract_downloaded_tables('publications_aanda')
    extract_downloaded_tables('publications_aanda/publications_aanda_tables')
    # extract_downloaded_tables('publications_iopscience')
    
main()