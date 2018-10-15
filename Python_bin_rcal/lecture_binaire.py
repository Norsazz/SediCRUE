import struct
import os
import xml.etree.ElementTree as ET
import random
import csv
import numpy
import copy
import time
import math

#procedure de recuperation des donnees du rcal.xlm pour lire le rcal.bin
def recuperation_donnees(fichier,repertoire,nom_cal):
    #chargement du fichier xml
    tree = ET.parse(str(os.path.join(repertoire,fichier)))
    root = tree.getroot()
    #variables a completer
    
    #taille des mots en nombre d octet pour le lecteur
    taille_mot=0

    #nombre de mot a lire avant d arriver a la partie section
    offset_section=0

    #position du lecteur de bin
    position=0

    #dictionnaire des calculs donnant les fichiers a traiter
    calcul_info_fic=dict()

    #dictionnaire des calculs donnant les positions (nombre de mot) de chaque calcul dans le .bin
    calcul_info_offset=dict()

    #dictionnaire reliant une section a sa position dans le .bin
    pos_section=dict()

    #position de la variable z
    position_z=0

    #nombre de mot total pour un calcul permanent
    nb_mot_cal=0
    
    #nombre de variables total
    nb_var=0
    
    nb=0

    #boucle pour trouver le nombre d octet par mot
    for rank in root.iter('{http://www.fudaa.fr/xsd/crue}NbrOctetMot'):
        taille_mot=int(float(rank.text))

    #boucle  pour trouver le nombre de mot par calcul
    for rank in root.iter('{http://www.fudaa.fr/xsd/crue}StructureResultat'):
        nb_mot_cal=int(float(rank.get("NbrMot")))
        #calcul de la position de la rubrique section dans le .bin
        for rank2 in rank.getchildren():
            if rank2.tag!="{http://www.fudaa.fr/xsd/crue}Sections":
                #augmentation de l offset
                offset_section=offset_section+int(float(rank2.get("NbrMot")))
            else:
                #boucle pour calculer le nombre de variable et la position de la variable etudiee
                for rank3 in rank2.iter('{http://www.fudaa.fr/xsd/crue}VariableRes'):
                    nb=nb+1
                    if (rank3.get('NomRef')=="Z" ):
                        position_z=nb
                        nb_var=nb_var+1
                    else:
                        nb_var=nb_var+1
                i=0
                #on estime la position du lecteura partir de l offset
                position=offset_section+2 # offset de 2 car il y a le nom de la section et le RcalP au debut du fichier
                #boucle pour remplir le dictionnaire section-position dans le bin
                for rank3 in rank2.getchildren():
                    if rank3.tag=="{http://www.fudaa.fr/xsd/crue}SectionIdem"or rank3.tag=="{http://www.fudaa.fr/xsd/crue}SectionSansGeometrie":
                        for rank4 in rank3.getchildren():
                            position=position+int(float(rank4.get('NbrMot')))
                    else:
                        for rank4 in rank3.getchildren():
                                nom_section=rank4.get('NomRef')
                                pos_section[position+position_z-1]=nom_section
                                position=position+nb_var
                break
    i=0

    nom_cal2=list()
    index=list()
    ind=dict()
    #boucle pour remplir les informations sur les calculs les offset et les fichiers
    for rank in root.iter("{http://www.fudaa.fr/xsd/crue}ResCalcPseudoPerm"):
        fic_cal=rank.get("Href")
        offset_cal=rank.get("OffsetMot")
        nom_ref=rank.get("NomRef")
        if(nom_ref in nom_cal):
            nom_cal2.append(nom_ref)
            index.append(nom_cal.index(nom_ref))
            i=i+1
        calcul_info_fic[nom_ref]=str(repertoire+"/"+fic_cal)
        calcul_info_offset[nom_ref]=offset_cal
    for i in range(len(index)):
        ind[index[i]]=i
    for i in range(len(index)):
        index[i]=ind[i]
    return pos_section,calcul_info_fic,calcul_info_offset,nom_cal2,taille_mot,index

def recuperation_donnees_trans(fichier,repertoire,nom_cal):
    #chargement du fichier xml
    tree = ET.parse(str(os.path.join(repertoire,fichier)))
    root = tree.getroot()
    #variables a completer
    
    #taille des mots en nombre d octet pour le lecteur
    taille_mot=0

    #nombre de mot a lire avant d arriver a la partie section
    offset_section=0

    #position du lecteur de bin
    position=0

    #dictionnaire des calculs donnant les fichiers a traiter
    calcul_info_fic=dict()

    #dictionnaire des calculs donnant les positions (nombre de mot) de chaque calcul dans le .bin
    calcul_info_offset=dict()
    calcul_info_temps=dict()
    #dictionnaire reliant une section a sa position dans le .bin
    pos_section=dict()

    #position de la variable z
    position_z=0

    #nombre de mot total pour un calcul permanent
    nb_mot_cal=0
    
    #nombre de variables total
    nb_var=0
    
    nb=0

    #boucle pour trouver le nombre d octet par mot
    for rank in root.iter('{http://www.fudaa.fr/xsd/crue}NbrOctetMot'):
        taille_mot=int(float(rank.text))

    #boucle  pour trouver le nombre de mot par calcul
    for rank in root.iter('{http://www.fudaa.fr/xsd/crue}StructureResultat'):
        nb_mot_cal=int(float(rank.get("NbrMot")))
        #calcul de la position de la rubrique section dans le .bin
        for rank2 in rank.getchildren():
            if rank2.tag!="{http://www.fudaa.fr/xsd/crue}Sections":
                #augmentation de l offset
                offset_section=offset_section+int(float(rank2.get("NbrMot")))
            else:
                #boucle pour calculer le nombre de variable et la position de la variable etudiee
                for rank3 in rank2.iter('{http://www.fudaa.fr/xsd/crue}VariableRes'):
                    nb=nb+1
                    if (rank3.get('NomRef')==nom_cal ):
                        position_z=nb
                        nb_var=nb_var+1
                    else:
                        nb_var=nb_var+1
                i=0
                #on estime la position du lecteura partir de l offset
                position=offset_section+2 # offset de 2 car il y a le nom de la section et le RcalP au debut du fichier
                #boucle pour remplir le dictionnaire section-position dans le bin
                for rank3 in rank2.getchildren():
                    if rank3.tag=="{http://www.fudaa.fr/xsd/crue}SectionIdem"or rank3.tag=="{http://www.fudaa.fr/xsd/crue}SectionSansGeometrie":
                        for rank4 in rank3.getchildren():
                            position=position+int(float(rank4.get('NbrMot')))
                    else:
                        for rank4 in rank3.getchildren():
                                nom_section=rank4.get('NomRef')
                                pos_section[position+position_z-1]=nom_section
                                position=position+nb_var
                break
    i=0

    nom_cal2=list()
    index=list()
    ind=dict()
    #boucle pour remplir les informations sur les calculs les offset et les fichiers
    for rank2 in root.iter("{http://www.fudaa.fr/xsd/crue}ResCalcTrans"):
        nom_ref=rank2.get("NomRef")
        nom_cal2.append(nom_ref)
        fic_cal=list()
        offset_cal=list()
        temps=list()
        for rank in rank2.iter("{http://www.fudaa.fr/xsd/crue}ResPdt"):
            fic_cal.append(str(repertoire+"/"+rank.get("Href")))
            offset_cal.append(rank.get("OffsetMot"))
            temps.append(conversion_temps(rank.get("TempsSimu")))
        temp=numpy.array(temps)
        temp.astype(float)
        temp=temp-temp[0]
        temp.astype(int)
        temps=list(temp)
        calcul_info_fic[nom_ref]=fic_cal
        calcul_info_offset[nom_ref]=offset_cal
        calcul_info_temps[nom_ref]=temps
    return pos_section,calcul_info_fic,calcul_info_offset,calcul_info_temps,nom_cal2,taille_mot

def conversion_temps(a):
    temps=0
    b=str(a)
    if(b[0]=="P"):
        if(b[2]=="D"):
            temps=temps+3600*24*float(b[1])
            b=b[2:]
        else:
            temps=temps+3600*24*float(str(b[1]+b[2]))
            b=b[3:]
    if(b[0]=="D"):
        if(b[3]=="H"):
            temps=temps+3600*float(b[2])
            b=b[3:]
        else:
            temps=temps+3600*float(str(b[2]+b[3]))
            b=b[4:]
    if(b[0]=="H"):
        if(b[2]=="M"):
            temps=temps+60*float(b[1])
            b=b[2:]
        else:
            temps=temps+60*float(str(b[1]+b[2]))
            b=b[3:]
    if(b[0]=="M"):
        if(b[2]=="S"):
            temps=temps+float(b[1])
            b=b[2:]
        else:
            temps=temps+float(str(b[1]+b[2]))
            b=b[3:]
    return int(temps)

def ecriture_resultat_trans(pos_section,calcul_info_fic,calcul_info_offset,calcul_info_temps,nom_cal,dico_section):

    #definition de la liste des position et triage par ordre croissant de la liste resultante pour extraire les resultats avec une liste de sections conforme
    l_cle=list()
    for cle in pos_section:
        l_cle.append(cle)

    l_cle.sort()
    i=0
    nb_mot=0
    j=0
    k=0
    #resultat qui a une section associe la liste des resultats de chaque calcul de la liste nom_cal
    resultat=dict()
    
    #initialisation du dictionnaire de resultat sous forme de listes
    for sec in nom_cal:
        liste=dict()
        resultat[sec]=liste
        for test in dico_section[sec]:
            resultat[sec][test]=list()
    offsets=list()
    #liste des offsets dans l ordre des calculs (qui sont dans l ordre d execution de fudaa-crue et nomenclature fudaa Cc_Pxx sinon plantage)
    fichiers=list()
    for l in range(len(nom_cal)):
        offsets.append(calcul_info_offset[nom_cal[l]])
        fichiers=fichiers+calcul_info_fic[nom_cal[l]]
    #liste des fichiers bin a lire dans l ordre des calculs
    fichiers=list(set(fichiers))
    fichiers.sort()
    l=0
    m=0
    k=0
    #boucle de lectures des fichiers binaires resultants
    while j<len(nom_cal):
        for fic in fichiers:
            #print fic,m,l,k,offsets[j][m]
            f = open(fic, "rb")
            #try catch pour ne planter le programme a la lecture
            try:
                while(j<len(nom_cal) and l<len(l_cle)):
                    s = struct.Struct("<d") # format des donnees binaires a lire ici que des double de 8 octets
                    #boucle tant que l on a pas lu tous les calculs des fichiers
                    #lecture des octets en dur selon le nombre d octet utilise par mot
                    record = f.read(8)
                    #si taille differente on saute au paquet suivant
                    if len(record) != 8:
                        break;
                    #test si la position courante correspond a la position d une section
                    if  i==l_cle[l]+int(float(offsets[j][m])):
                        #print offsets[j][m],i,m,len(calcul_info_temps[nom_cal[j]])
                        if (pos_section[l_cle[l]] in dico_section[nom_cal[j]]):
                            #decodage de l octet
                            a=s.unpack(record)
                            #on affecte la valeur a la liste de hauteur pour la position
                            resultat[nom_cal[j]][pos_section[l_cle[l]]].append(a[0])
                            k=k+1
                            #test si l on a fini un calcul
                            if(k>=len(dico_section[nom_cal[j]])):
                                l=0
                                k=0
                                m=m+1
                                #print m,j
                                #print m>=len(calcul_info_temps[nom_cal[j]])
                                #print calcul_info_fic[nom_cal[j]][m]!=calcul_info_fic[nom_cal[j]][m-1]
                                if(m>=len(calcul_info_temps[nom_cal[j]])):
                                    bool_test=False
                                    if(j+1>=len(nom_cal)):
                                        bool_test=True
                                    else:
                                        if(calcul_info_fic[nom_cal[j]][m-1]!=calcul_info_fic[nom_cal[j+1]][0]):
                                            bool_test=True
                                    if(bool_test):
                                        m=0
                                        i=0
                                        j=j+1
                                        f.close()
                                        break
                                    else:
                                        m=0                        
                                        j=j+1
                                else:
                                    if(calcul_info_fic[nom_cal[j]][m]!=calcul_info_fic[nom_cal[j]][m-1]):
                                        i=0
                                        f.close()
                                        break
                        l=l+1
                    i=i+1              
                    

            except IOError:
                pass
            finally:
                f.close()

    #ecriture des resultats
    #choix arbitraire du nom test.csv
    fic="test.csv"
    f=open(fic,"wb")
    cr=csv.writer(f,delimiter=";")
    # on trie les sections
    #pour refaire meme template que le rapport csv de fudaa 
    for i in range(4):
        cr.writerow(" ")
    
                                   
    #ecriture des sections hauteur mesurees des calculs par sections
    for j in range(len(nom_cal)):          
        cr.writerow(["calcul","temps"]+dico_section[nom_cal[j]])
        for n in range(len(calcul_info_temps[nom_cal[j]])):
            #resort du fichier resultat
            dummy=list()
            for k in range(len(dico_section[nom_cal[j]])):
                dummy.append(resultat[nom_cal[j]][dico_section[nom_cal[j]][k]][n])
            cr.writerow([str(nom_cal[j])]+[str(calcul_info_temps[nom_cal[j]][n])]+dummy)
    f.close()

    return resultat,calcul_info_temps

def calcul_crit(temps,valeurs):
        lmax=0
        vol=0
        tps_max=0
        lmax=max(valeurs)
        indice_max=list()
        for j in range(len(temps)):
            if(lmax==valeurs[j]):
                indice_max.append(temps[j])
            if(j>0):
                vol=vol+(valeurs[j]+valeurs[j])/2.0*(temps[j]-temps[j-1])
        tps_max=max(indice_max)
        return lmax,vol,tps_max

def calcul_crit_nash_hauteur(res_ref,res_cal,temps1,temps2):
    dico_ref=dict()
    dico_cal=dict()
    dico_cal_vrai=dict()
    CNash=1
    Chauteur=0
    for i in range(len(temps1)):
        dico_ref[temps1[i]]=res_ref[i]
    for i in range(len(temps2)):
        dico_cal[temps2[i]]=res_cal[i]
    temps_concat=[val for val in temps1 if val in temps2]
    for i in range(len(temps_concat)):
        dico_cal_vrai[temps_concat[i]]=0.0
    hmax=max([dico_ref[temps1[i]] for i in range(len(temps1))])
    hmax2=max([dico_cal[temps2[i]] for i in range(len(temps2))])
    i=0
    j=0
    while(i<len(temps_concat)):
        if(i>0):
            effectif=0
            while (j<len(temps2) and temps2[j]<=temps_concat[i] and temps2[j]>temps_concat[i-1]):
                dico_cal_vrai[temps_concat[i]]=dico_cal_vrai[temps_concat[i]]+dico_cal[temps2[j]]
                effectif=effectif+1
                j=j+1
            dico_cal_vrai[temps_concat[i]]=dico_cal_vrai[temps_concat[i]]/effectif
            i=i+1
        else:
            dico_cal_vrai[temps_concat[i]]=dico_cal[temps2[i]]
            i=i+1
            j=j+1
    ecart1=0
    ecart2=0
    ecart3=0
    for i in range(len(temps_concat)):
        if(i==0):
            ecart1=ecart1+(dico_cal_vrai[temps_concat[i]]-dico_ref[temps_concat[i]])**2
            ecart2=ecart2+(dico_cal_vrai[temps_concat[i]]-dico_ref[temps_concat[i+1]])**2
        elif(i==len(temps_concat)-1):
            ecart1=ecart1+(dico_cal_vrai[temps_concat[i]]-dico_ref[temps_concat[i]])**2
            ecart3=ecart3+(dico_cal_vrai[temps_concat[i]]-dico_ref[temps_concat[i-1]])**2
        else:
            ecart1=ecart1+(dico_cal_vrai[temps_concat[i]]-dico_ref[temps_concat[i]])**2
            ecart3=ecart3+(dico_cal_vrai[temps_concat[i]]-dico_ref[temps_concat[i-1]])**2
            ecart2=ecart2+(dico_cal_vrai[temps_concat[i]]-dico_ref[temps_concat[i+1]])**2
    ecart1=math.sqrt(ecart1/len(temps_concat))*100.0
    ecart2=math.sqrt(ecart2/(len(temps_concat)-1))*100.0
    ecart3=math.sqrt(ecart3/(len(temps_concat)-1))*100.0
    ecart_f=min(ecart1,min(ecart2,ecart3))
    hmax=abs(hmax-hmax2)*100.0
    return hmax,CNash,Chauteur,ecart_f


def calcul_quad_trans(res_ref,res_cal,temps1,temps2):
    dico_ref=dict()
    dico_cal=dict()
    dico_cal_vrai=dict()
    for i in range(len(temps1)):
        dico_ref[temps1[i]]=res_ref[i]
    for i in range(len(temps2)):
        dico_cal[temps2[i]]=res_cal[i]
    temps_concat=[val for val in temps1 if val in temps2]
    for i in range(len(temps_concat)):
        dico_cal_vrai[temps_concat[i]]=0.0
    hmax=max([dico_ref[temps1[i]] for i in range(len(temps1))])
    hmax2=max([dico_cal[temps2[i]] for i in range(len(temps2))])
    i=0
    j=0
    while(i<len(temps_concat)):
        if(i>0):
            effectif=0
            while (j<len(temps2) and temps2[j]<=temps_concat[i] and temps2[j]>temps_concat[i-1]):
                dico_cal_vrai[temps_concat[i]]=dico_cal_vrai[temps_concat[i]]+dico_cal[temps2[j]]
                effectif=effectif+1
                j=j+1
            dico_cal_vrai[temps_concat[i]]=dico_cal_vrai[temps_concat[i]]/effectif
            i=i+1
        else:
            dico_cal_vrai[temps_concat[i]]=dico_cal[temps2[i]]
            i=i+1
            j=j+1
    ecart1=0
    ecart2=0
    ecart3=0
    for i in range(len(temps_concat)):
        if(i==0):
            ecart1=ecart1+(dico_cal_vrai[temps_concat[i]]-dico_ref[temps_concat[i]])**2
            ecart2=ecart2+(dico_cal_vrai[temps_concat[i]]-dico_ref[temps_concat[i+1]])**2
        elif(i==len(temps_concat)-1):
            ecart1=ecart1+(dico_cal_vrai[temps_concat[i]]-dico_ref[temps_concat[i]])**2
            ecart3=ecart3+(dico_cal_vrai[temps_concat[i]]-dico_ref[temps_concat[i-1]])**2
        else:
            ecart1=ecart1+(dico_cal_vrai[temps_concat[i]]-dico_ref[temps_concat[i]])**2
            ecart3=ecart3+(dico_cal_vrai[temps_concat[i]]-dico_ref[temps_concat[i-1]])**2
            ecart2=ecart2+(dico_cal_vrai[temps_concat[i]]-dico_ref[temps_concat[i+1]])**2
    ecart1=math.sqrt(ecart1/len(temps_concat))*100.0
    ecart2=math.sqrt(ecart2/(len(temps_concat)-1))*100.0
    ecart3=math.sqrt(ecart3/(len(temps_concat)-1))*100.0
    ecart_f=min(ecart1,min(ecart2,ecart3))
    return ecart_f

def calcul_hmax_trans(res_ref,res_cal,temps1,temps2):
    hmax=max([res_ref[i] for i in range(len(res_ref))])
    hmax2=max([res_cal[i] for i in range(len(res_cal))])
    hmax=abs(hmax-hmax2)*100
    return hmax

def calcul_vol_trans(res_ref,res_cal,temps1,temps2):
    vol1=0
    vol2=0
    for i in range(len(temps1)-1):
        vol1=vol1+(res_ref[i+1]+res_ref[i])*0.5*(temps1[i+1]-temps1[i])
    for i in range(len(temps2)-1):
        vol2=vol2+(res_cal[i+1]+res_cal[i])*0.5*(temps2[i+1]-temps2[i])
    dvol=abs(vol1-vol2)
    return dvol
   
        
def resultat_crit_Nash(res_ref,temps1,res_cal,temps2,nom_cal,dico_section):
    resu=dict()
    for sec in nom_cal:
        resu[sec]=dict()
        for test in dico_section[sec]:
            resu[sec][test]=list(calcul_crit_nash_hauteur(res_ref[sec][test],res_cal[sec][test],temps1[sec],temps2[sec]))
    hmax=0
    CNash=0
    Chauteur=0
    ecart_quad=0
    dmax=list()
    dn=list()
    dh=list()
    decart=list()
    effectif=0
    for sec in nom_cal:
        dhmax=list()
        dCN=list()
        dCH=list()
        dEC=list()
        for test in dico_section[sec]:
            effectif=effectif+1
            a=resu[sec][test]
            hmax=hmax+a[0]
            CNash=CNash+a[1]
            Chauteur=Chauteur+a[2]
            ecart_quad=ecart_quad+a[3]
            dhmax.append(a[0])
            dCN.append(a[1])
            dCH.append(a[2])
            dEC.append(a[3])
        dmax.append(dhmax)
        dn.append(dCN)
        dh.append(dCH)
        decart.append(dEC)
        ecart_quad=ecart_quad/effectif
        hmax=hmax/effectif
        CNash=CNash/effectif
        Chauteur=Chauteur/effectif
    
    return resu,hmax,CNash,Chauteur,ecart_quad,dmax,dn,dh,decart

def resultat_crit_trans(res_ref,temps1,res_cal,temps2,nom_cal,dico_section,strcrit):
    if(strcrit=="v"):
        critere=calcul_vol_trans
    elif(strcrit=="h"):
        critere=calcul_hmax_trans
    else:
        critere=calcul_quad_trans
    resu=dict()
    for sec in nom_cal:
        resu[sec]=dict()
        for test in dico_section[sec]:
            resu[sec][test]=critere(res_ref[sec][test],res_cal[sec][test],temps1[sec],temps2[sec])
    val=0
    val_liste=list()
    effectif=0
    for sec in nom_cal:
        dval=list()
        for test in dico_section[sec]:
            effectif=effectif+1
            a=resu[sec][test]
            val=val+a
            dval.append(a)
        val_liste.append(dval)
        val=val/effectif
    return resu,val,val_liste

def resultat_crit(resultat,calcul_info_temps,nom_cal,dico_section):
    resu=dict()
    for sec in nom_cal:
        resu[sec]=dict()
        for test in dico_section[sec]:
            resu[sec][test]=list(calcul_crit(calcul_info_temps[sec],resultat[sec][test]))
    return resu


#fonction pour ecrire les resultats souhaites
def ecriture_resultat(pos_section,calcul_info_fic,calcul_info_offset,nom_cal,dico_dist,nom_cal2,index):

    #definition de la liste des position et triage par ordre croissant de la liste resultante pour extraire les resultats avec une liste de sections conforme
    l_cle=list()
    for cle in pos_section:
        l_cle.append(cle)

    l_cle.sort()
    i=0
    nb_mot=0
    j=0
    k=0
    #resultat qui a une section associe la liste des resultats de chaque calcul de la liste nom_cal
    resultat=dict()

    #initialisation du dictionnaire de resultat sous forme de listes
    for sec in pos_section.values():
        liste=list()
        resultat[sec]=liste
    offsets=list()
    #liste des offsets dans l ordre des calculs (qui sont dans l ordre d execution de fudaa-crue et nomenclature fudaa Cc_Pxx sinon plantage) 
    for l in range(len(nom_cal2)):
        offsets.append(calcul_info_offset[nom_cal2[l]])
    #liste des fichiers bin a lire dans l ordre des calculs 
    fichiers=list(set(calcul_info_fic.values()))
    fichiers.sort()

    #boucle de lectures des fichiers binaires resultants  
    for fic in fichiers:
        f = open(fic, "rb")
        #try catch pour ne planter le programme a la lecture
        try:
            s = struct.Struct("<d") # format des donnees binaires a lire ici que des double de 8 octets
            #boucle tant que l on a pas lu tous les calculs des fichiers
            while j<len(l_cle):
                #lecture des octets en dur selon le nombre d octet utilise par mot
                record = f.read(8)
                #si taille differente on saute au paquet suivant
                if len(record) != 8:
                    break;
                #test si la position courante correspond a la position d une section  
                if  i==l_cle[j]+int(float(offsets[k])):
                    #decodage de l octet
                    a=s.unpack(record)
                    #on affecte la valeur a la liste de hauteur pour la position
                    resultat[pos_section[l_cle[j]]].append(a[0])
                    j=j+1
                    #test si l on a fini un calcul
                    if(j+1>len(l_cle)):
                        #on remet la position calcul a 0
                        j=0
                        #on passe au calcul suivant
                        k=k+1
                        # si on a plus de calcul break
                        if(k+1>len(offsets)):
                            i=0
                            break
                        #si le fichier courant ne correspond pas a celui du calcul suivant on change de fichier avec break
                        elif fic!=calcul_info_fic[nom_cal2[k]]:
                            i=0
                            break
                i=i+1
                

        except IOError:
                pass
        finally:
            f.close()

    #ecriture des resultats
    #choix arbitraire du nom test.csv
    fic="test.csv"
    f=open(fic,"wb")
    cr=csv.writer(f,delimiter=";")
    # on trie les sections
    liste_sect_sorted=list(pos_section.values())
    liste_sect_sorted.sort()
    #pour refaire meme template que le rapport csv de fudaa 
    for i in range(4):
        cr.writerow(" ")
    #ecriture des sections abscisses et hauteur mesurees des calculs par sections
    cr.writerow(["sections","X"]+nom_cal)
    for n in range(len(liste_sect_sorted)):
        #resort du fichier resultat
        dummy=list(resultat[liste_sect_sorted[n]])
        for k in range(len(resultat[liste_sect_sorted[n]])):
            resultat[liste_sect_sorted[n]][k]=dummy[index[k]]
        if ( True in [liste_sect_sorted[n].find(dico_dist.keys()[l])>-1 for l in range(len(dico_dist.keys()))]):
            for m in range(len(dico_dist.keys())):
                if liste_sect_sorted[n].find(dico_dist.keys()[m])>-1 :
                    cr.writerow([liste_sect_sorted[n],dico_dist[dico_dist.keys()[m]]]+resultat[liste_sect_sorted[n]])
                    break
        else:
            #si pas d information sur la distance au barrage alors on met valeur nulle
            cr.writerow([liste_sect_sorted[n],"0"]+resultat[liste_sect_sorted[n]])
    f.close()

    
#fichier="SB2013_zone_trans.rcal.xml"
#repertoire='C:/Projets/modeles_actualisation/test_lecture_binaire'
#res=recuperation_donnees_trans(fichier,repertoire,"Z")
#pos_section,calcul_info_fic,calcul_info_offset,calcul_info_temps,nom_cal2,taille_mot
#dico_section=dict()
#dico_section[res[4][0]]=["St_P91.250","St_P97.700"]
#resultat=ecriture_resultat_trans(res[0],res[1],res[2],res[3],res[4],dico_section)
#resu=resultat_crit(resultat[0],res[3],res[4],dico_section)
#nom_cal=["Cc_P06","Cc_P09","Cc_P13","Cc_P42","Cc_P46","Cc_P49","Cc_P08","Cc_P10"]
#res=recuperation_donnees(fichier,repertoire,nom_cal)
#ecriture_resultat(res[0],res[1],res[2],nom_cal)
#res=conversion_temps("P26DT0H0M0S")
#res
