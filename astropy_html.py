import time
import astropy.io.ascii as ascii

def main():
    mrt_titles = ['ajacdd6ft1_mrt.txt','ajacdd6ft5_mrt.txt','apjacd250t2_mrt.txt']
    # html_titles = ['EXPRES_IV_Two_Additional_Planets_Orbiting_ρ_Coronae_Borealis_Reveal_Uncommon_System_Architecture_IOPscience.html','Testing_the_Linear_Relationship_between_Black_Hole_Mass_and_Variability_Timescale_in_Low-luminosity_AGNs_at_Submillimeter_Wavelengths_-_IOPscience.html']
    for mrt_title in mrt_titles:
        file = open(mrt_title)
        content = file.read()
        start = time.time()
        astropy_table = ascii.read(content, format='cds') 
        end = time.time()
        print(f'Content of {mrt_title}')
        print(astropy_table)
        print(f'Time needed to read {mrt_title} is {str(end - start)} seconds.')
       
    
main() 