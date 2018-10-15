# -*- coding:Latin-1 -*-
import os
import xml.etree.ElementTree as ET
import random
import csv
import numpy
import copy



#Fonction qui initialise la fenetre des stricklers automatiquement
def init_strickler_fenetre(fichier,fenetre):
    #Chargement des Stricklers du xml dfrt
    tree = ET.parse(fichier)
    root = tree.getroot()
    Init_stricklers=list()
    Max_stricklers=list()
    Min_stricklers=list()
    Min_Maj_stricklers=list()
    
    for rank in root.iter('{http://www.fudaa.fr/xsd/crue}LoiFF'):
        if (rank.get('Nom').find("MIN")>-1):
            Min_Maj_stricklers.append(0)
        else:
            Min_Maj_stricklers.append(1)
    for rank in root.iter('{http://www.fudaa.fr/xsd/crue}LoiFF'):
        i=0
        for rank3 in rank.iter('{http://www.fudaa.fr/xsd/crue}PointFF'):
            if(i==0):
                new_rank = rank3.text.split(" ")
                rank_2 = float(new_rank[1])
                if (rank_2-fenetre>0):
                    Max_stricklers.append(float(rank_2)+float(fenetre))
                    Min_stricklers.append(float(rank_2)-float(fenetre))
                    Init_stricklers.append(float(rank_2))
                else:
                    Max_stricklers.append(0)
                    Min_stricklers.append(0)
                    Init_stricklers.append(float(rank_2))
            i=i+1
                

    return Max_stricklers,Min_stricklers,Init_stricklers,Min_Maj_stricklers




#Fonction tirant de nouveaux parametres de stricklers selon bornes choisies
def tirage_alea(Max_stricklers,Min_stricklers):
    new_strickler=list()
    for l in range(len(Max_stricklers)):
        if (Max_stricklers[l]<=Min_stricklers[l]):
            new_strickler.append(Max_stricklers[l])
        else:
            new_strickler.append(random.randrange(Min_stricklers[l],Max_stricklers[l]+1))
    return new_strickler



def change_strickler_loi(nv_str,fichier,loi):
    #Changement des Stricklers dans le xml dfrt
    new_strickler=list()
    tree = ET.parse(fichier)
    ET.register_namespace("","http://www.fudaa.fr/xsd/crue")
    root = tree.getroot()
    i=0
    dico_loi=dict()
    for rank1 in root.iter('{http://www.fudaa.fr/xsd/crue}LoiFF'):
        j=0
        test=[rank1.get("Nom").find(loi[k])>-1 for k in range(len(loi))]
        if(True in test):
            i=0
            for k in range(len(loi)):
                if(test[k]==True) :
                    i=k
                    break
            for rank in rank1.iter('{http://www.fudaa.fr/xsd/crue}PointFF'):
                if(j==0):
                    new_rank = rank.text.split(" ")
                    rank_1 = new_rank[0]
                    if (nv_str[i]<1):
                        rank_2=str(float(new_rank[1]))
                    else:
                        rank_2 = str(float(nv_str[i]))
                    new_strickler.append(rank_2)
                    new_rank=[rank_1,rank_2]
                    new_rank=" ".join(new_rank)
                    rank.text = str(new_rank)
                else:
                    new_rank = rank.text.split(" ")
                    rank_1 = new_rank[0]
                    new_rank=[rank_1,rank_2]
                    new_rank=" ".join(new_rank)
                    rank.text=str(new_rank)
    #Ecriture du nouveau xml
    tree.write(fichier)
    
# Fonction lisant dans le fichier csv exporte par otfa le numero de calculs associes aux lignes d eau etudiee 
def lire_calcul(fichier):
    fic=open(fichier,"rb")
    nom_calcul=list()
    cr = csv.reader(fic,delimiter=";")
    j=0
    for row in cr:
        if(j==4):
            for l in range(len(row)-2):
                nom_calcul.append(row[l+2])
                j=j+1
        elif(j<4):
            j=j+1
        else:
            break
    return nom_calcul

#Fonction qui a partir du nom des calculs et du nom des conditions aux limites donne la fourchette (+-10%) et les debits initiaux des lignes d eau
def initial_debit(fichier,nom_calcul,nom_cl):
    nb_cl=len(nom_cl)
    nb_cal=len(nom_calcul)
    init_debit=numpy.zeros((nb_cal,nb_cl))
    Max_debit=numpy.zeros((nb_cal,nb_cl))
    Min_debit=numpy.zeros((nb_cal,nb_cl))
    #Copie de l'architecture du xml dfrt
    tree = ET.parse(fichier)
    root = tree.getroot()
    i=0
    
    for rank in root.iter("{http://www.fudaa.fr/xsd/crue}CalcPseudoPerm"):
        if (nom_calcul[i].find(rank.get("Nom"))>0):
            j=0
            for rank2 in rank.iter("{http://www.fudaa.fr/xsd/crue}CalcPseudoPermNoeudQapp"):
                if(rank2.get("NomRef")==nom_cl[j]):
                    init_debit[i,j]=float(rank2.find("{http://www.fudaa.fr/xsd/crue}Qapp").text)
                    if(j<nb_cl-1):
                        j=j+1
                    else:
                        break
            if (i<nb_cal-1):
                i=i+1
            else:
                break
    for l in range(nb_cal):
        for k in range(nb_cl):
            Max_debit[l,k]=init_debit[l,k]+init_debit[l,k]*0.1
            Min_debit[l,k]=init_debit[l,k]-init_debit[l,k]*0.1
            
    return Max_debit,Min_debit,init_debit



#Fonction qui a partir d un tableau de debit va changer les debits du dclm 
#Donner les calculs et les condition limites dans l ordre fudaa...
def change_debit(new_debit,fichier,nom_calcul,nom_cl,):
    nb_cal=new_debit.shape[1]
    nb_cl=new_debit.shape[0]
    #Copie de l'architecture du xml dfrt
    tree = ET.parse(fichier)
    ET.register_namespace("","http://www.fudaa.fr/xsd/crue")
    root = tree.getroot()
    i=0
    while (i<nb_cal):
        for rank in root.iter("{http://www.fudaa.fr/xsd/crue}CalcPseudoPerm"):
            if (nom_calcul[i].find(rank.get("Nom"))>0):
                j=0
                for rank2 in rank.iter("{http://www.fudaa.fr/xsd/crue}CalcPseudoPermNoeudQapp"):
                    if(rank2.get("NomRef")==nom_cl[j]):
                        rank2.find("{http://www.fudaa.fr/xsd/crue}Qapp").text=str(float(new_debit[j,i]))
                        if(j<nb_cl-1):
                            j=j+1
                        else:
                            break
                if (i<nb_cal-1):
                    i=i+1
                else:
                    i=i+1
                    break
            
    tree.write(fichier)
    
#Fonction rendant une valeur aleatoire entre le reel a et b
def rand_real(a,b):
    result=0
    if(a==b):
        return a
    else:
        rdom=random.random()
        result=float(a+rdom*(b-a))
        return result
    
        
#Fonction qui tire des valeurs de debit entre les bornes debits min et debits max
def tirage_debit(debit_min,debit_max):
    nb_cal=debit_min.shape[0]
    nb_cl=debit_min.shape[1]
    new_debit=numpy.zeros(debit_min.shape)
    for l in range(nb_cal):
        for k in range(nb_cl):
            new_debit[l,k]=rand_real(debit_min[l,k],debit_max[l,k])
    return new_debit

#Fonction qui permet d'activer ou de desactiver plusieurs condition sur le dclm.xml
#On donne a chaque fois la liste (! donner imperativement une liste meme pour 1 element) des types de cond calcPermNoeuds... pour chaque condition
#Donner les noms de references correspondants
#Donner les booleens d activation correspondants (true=activation)
def Activation_CL(fichier,fichier2,Type_cond,Nom_cond,ifActive):
    tree = ET.parse(fichier)
    ET.register_namespace("","http://www.fudaa.fr/xsd/crue")
    root = tree.getroot()
    nb_type=len(Type_cond)
    for i in range(nb_type):
        for rank in root.iter(str("{http://www.fudaa.fr/xsd/crue}"+Type_cond[i])):
            if (rank.get("NomRef")==Nom_cond[i]):
                print rank.attrib
                if (ifActive[i]):
                    rank.find("{http://www.fudaa.fr/xsd/crue}IsActive").text="true"
                else:
                    rank.find("{http://www.fudaa.fr/xsd/crue}IsActive").text="false"
   
    tree.write(fichier2)
    
#Fonction qui permet de creer une condition initiale pour tous les calculs en permanents dans le dclm.xml avec
#le type de la condition initiale (attention fudaa les lit dans dans l ordre donc pour les changements manuels ne pas mettre CL debit au noeud apres cote imposee le schema de lecture est comme suit:
    #NoeudQapp->NoeudZimp->BrancheOrifice->BrancheSaintVenant->CasierProfil)
#le nom de reference NomRef
#la liste des noms des sous_elements (sous forme de liste)
#le texte correspondant aux sous elem 
def Creation_CL(fichier,fichier2,Type_cond,nom_cond,nom_sous_elem,sous_elem_text):
    Liste_type_cal=["CalcPseudoPermNoeudQapp","CalcPseudoPermNoeudNiveauContinuZimp","CalcPseudoPermBrancheOrificeManoeuvre","CalcPseudoPermBrancheSaintVenantQruis","CalcPseudoPermCasierProfilQruis"]
    tree = ET.parse(fichier)
    ET.register_namespace("","http://www.fudaa.fr/xsd/crue")
    root = tree.getroot()
    for rank in root.iter(str("{http://www.fudaa.fr/xsd/crue}CalcPseudoPerm")):
        e=ET.Element(Type_cond,{"NomRef":nom_cond})
        for l in range(len(nom_sous_elem)):
            a=ET.SubElement(e,nom_sous_elem[l])
            a.text=sous_elem_text[l]
        rank.append(e)
        for j in range(len(Liste_type_cal)):
            for elem in rank.findall(str("{http://www.fudaa.fr/xsd/crue}"+Liste_type_cal[j])):
                dummy=copy.deepcopy(elem)
                rank.remove(elem)
                rank.append(dummy)
    tree.write(fichier2)


#test de verification
#sExeOtfa = "otfa-batch.bat"
#sArg = "test1.otfa.xml"
#temps_alloue=600
        
#fic_csv="resref1.csv"

#fichier="C:\Users\ROTHE\Desktop\modeles_actualisation\DM2013_cconc_ST1.dclm.xml"
#nom_cl=["Nd_NVR153.100","Nd_PCF1"]
#nom_calcul=lire_calcul(fic_csv)   

#nb_cl=len(nom_cl)
#nb_cal=len(nom_calcul)


#Copie de l'architecture du xml dfrt
#tree = ET.parse(fichier)
#ET.register_namespace("","http://www.fudaa.fr/xsd/crue")
#root = tree.getroot()
#i=0
    
#for rank in root.iter("{http://www.fudaa.fr/xsd/crue}CalcPseudoPerm"):
#    rank.append(ET.Element("CalcPseudoPermNoeudQapp",{"NomRef":"Nd_PCF1"}))
   
#Activation_CL(fichier,"test_clm.xml",["CalcPseudoPermNoeudQapp","CalcPseudoPermNoeudQapp"],nom_cl,[False,False])
#Creation_CL("C:\Projets\SB_tests\Etu_SB2013_Conc\SB2013_mod_phys.dclm.xml","C:\Projets\SB_tests\Etu_SB2013_Conc\SB2013_mod_phys.dclm.xml","{http://www.fudaa.fr/xsd/crue}CalcPseudoPermNoeudQapp","Nd_NRE64.800",["{http://www.fudaa.fr/xsd/crue}IsActive","{http://www.fudaa.fr/xsd/crue}Qapp"],["true","200"])       

fichier="SB2013_cconc_str.dptg.xml"
fic_csv="repart_strickler_1.csv"
fic_sortie="poubelle.xml"

def change_loi_frt(fichier,fic_csv,fic_sortie):
#routine pour changer liste des frottemznts pour chaque sections
    fic_mes=open(fic_csv,"rb")
    cr=csv.reader(fic_mes,delimiter=";")
    i=0
    liste_str=list()
    liste_p=list()
    for row in cr:
        liste_p.append(row[0])
        liste_str.append(row[1])
        i=i+1
    k=0
    print liste_str
    print liste_p
    print len(liste_str)
    print len(liste_p)
    tree = ET.parse(fichier)
    ET.register_namespace("","http://www.fudaa.fr/xsd/crue")
    root = tree.getroot()
    while(k<len(liste_p)):
        for rank in root.iter(str("{http://www.fudaa.fr/xsd/crue}ProfilSection")):
            if(k<len(liste_str) and liste_p[k].find(rank.get("Nom")[3:])>-1):
                print liste_p[k],k
                for rank2 in rank.iter(str("{http://www.fudaa.fr/xsd/crue}LitNumerotes")):
                    for rank3 in rank2.iter(str("{http://www.fudaa.fr/xsd/crue}LitNumerote")):
                        a=rank3.find("{http://www.fudaa.fr/xsd/crue}IsLitActif")
                        b=rank3.find("{http://www.fudaa.fr/xsd/crue}IsLitMineur")
                        c=rank3.find("{http://www.fudaa.fr/xsd/crue}Frot")
                        if(liste_str[k]!=""):
                            bool1=bool(a.text=="true")
                            bool2=bool(b.text=="true")
                            if(bool2):
                                c.set("NomRef",str("Fk_"+liste_str[k]+"min"))
                            elif (bool1):
                                c.set("NomRef",str("Fk_"+liste_str[k]+"maj"))
                        print c.get("NomRef")
                k=k+1
    tree.write(fic_sortie)

#change_loi_frt("DM2013_cconc_zone.dptg.xml","repart_strickler_1.csv","poubelle.xml")

                    
                    
                



