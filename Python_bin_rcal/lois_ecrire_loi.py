import xml.etree.ElementTree as ET


fichier="DM2013_cconc.dfrt.xml"
tree = ET.parse(fichier)
root = tree.getroot()
fic=open("lois.txt","wb")
ET.register_namespace("","http://www.fudaa.fr/xsd/crue")
for rank in root.iter("{http://www.fudaa.fr/xsd/crue}LoiFF"):
    print rank.get("Nom")
    fic.write(rank.get("Nom")+"\n")

fic.close()
    
                      

