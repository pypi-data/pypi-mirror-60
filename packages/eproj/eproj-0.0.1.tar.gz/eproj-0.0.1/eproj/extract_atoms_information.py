
import urllib.request

def get_protein(name_protein, file_protein_pdb):

    fileDownload = "https://files.rcsb.org/download/" + name_protein +".pdb"

    Download = urllib.request.urlopen(fileDownload)

    filee = open(file_protein_pdb, "wb")
    filee.write(Download.read())
    filee.close()