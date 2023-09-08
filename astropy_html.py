from bs4 import BeautifulSoup
import astropy.io.ascii as ascii

def main():
    file = open('Toy model for the acceleration of blazar jets _ Astronomy & Astrophysics (A&A).html', 'r')
    content = file.read()
    soup_content = BeautifulSoup(content, 'html.parser')
    table = soup_content.find('table')
    table_parent = table.parent.parent 
    astropy_table = ascii.read(content, format='html') 
    print(astropy_table)
    
main() 