#*-*- coding:Latin-1-*
import os
import string
import xml.etree.ElementTree as ET
import subprocess
import modif_stricklers_xml as modif
import comp_csv as crit
import time
import shutil
import numpy
import random
import math
import matplotlib.pyplot as plt
import csv
from scipy import special
import sys
import itertools
import struct
import lecture_binaire as lbin
import glob
import copy

# fonction pour faire un graphique avec un titre, le label des axes une legende et un format d'image de sortie
def plot(x,y,xlab,ylab,shape,titre,label,format_img):
    plt.figure()
    lineObjects=plt.plot(x,y,shape)
    plt.legend(lineObjects, label)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    nom=titre+"."+format_img
    plt.legend()
    plt.grid(True)
    plt.savefig(nom,format=format_img)
    plt.show(block=False) #pour faire en sorte que l image ne bloque pas l execution du programme
    #pour bloquer au cas ou le programme a la visualisation de l image 
    #os.system("pause")
    #plt.close()

 


#Fonction pour lancer fudaa à partir du fichier otfa
def lance_otfa(sExeOtfa,sArg):
    subprocess.check_call([ sExeOtfa,sArg],shell=False)
def lance_exe(arg):
    subprocess.check_call(arg,shell=False)
#fonction pour afficher et sauvegarder les images des lignes d eau calculees et mesurees
#(prend en arg distance mesuree, distance calculee, les valeurs corresondantes des lignes d'eau mesuree et calculee)
def plot_le(dist_mes,dist_mod,le_mes,le_cal):
    nb_ligne=len(le_mes[1,:])
    symbol="+x"
    color=["b","g","r","c","m","y","k"]
    lab="le"
    maxi=max(numpy.max(le_mes),numpy.max(le_cal))
    mini=min(numpy.min(le_mes[le_mes>0]),numpy.min(le_cal[le_cal>0]))
    plt.figure()
    for j in range(nb_ligne):
        plt.plot(dist_mes,le_mes[:,j],str(color[j%len(color)]+symbol[j%len(symbol)]))
        plt.plot(dist_mod,le_cal[:,j],str(color[j%len(color)]),label=str(lab+str(j)))
    plt.xlabel("PK")
    plt.ylabel("cote")
    plt.grid(True)
    plt.ylim((mini,maxi))
    plt.title("Ligne_eau_cal_mes")
    plt.legend()
    plt.savefig("Lignes_eau.png",format="png")
    plt.show(block=False)
    #os.system("pause")
    #plt.close()
    
#Fonction pour appliquer la méthode de Montecarlo aux stricklers
def Montecarlo(sExeOtfa,sArg,fichier,fichier2,fichier3,fichier4,fic_csv2,temps_alloue,fic_excel,ponderation,chemin_crue_10,nom_cal,nom_ecart):
    #Procédure de Montecarlo
    debut=time.time()
    #Copie du fichier strickler initial
    if(fichier2!=fichier):
        shutil.copyfile(fichier2,fichier)
    if(fichier3!=fichier4):
        shutil.copyfile(fichier3,fichier4)

    
    resultat=crit.import_Stricklers(fic_excel)
    Max_stricklers=resultat[3]
    Min_stricklers=resultat[2]
    Init_stricklers=resultat[1]
    nom_loi=resultat[0]
    
    resultat=crit.import_le_mesure(fic_excel)
    le_mes=resultat[1]
    pk=resultat[0]

    resultat=crit.import_debit(fic_excel)
    nom_calcul=modif.lire_calcul(fic_csv2)
    nom_cl=resultat[3]
    Max_debit=resultat[2]
    Min_debit=resultat[1]
    Init_debit=resultat[0]
    #extraction de "CC_Pxx"
    nom_calcul2=list(nom_calcul)
    for l in range(len(nom_calcul2)):
        nom_calcul2[l]=nom_calcul2[l][4:]
    # test parametres initiaux
    modif.change_strickler_loi(Init_stricklers,fichier,nom_loi)
    modif.change_debit(Init_debit,fichier4,nom_calcul,nom_cl)
    
    lance_otfa(sExeOtfa,sArg)
    res=crit.extraction_csv_comp(pk,le_mes,fic_csv2,nom_cal,nom_ecart)
    dico_dist=res[4]
    #Choix de la fonction critere a appliquer
    #a=crit.fonc_crit_moyenne_abs(res[0],res[1])
    a=crit.fonc_crit_moyenne_quad(res[0],res[1],ponderation)
    #a=crit.fonc_crit_moyenne_max(res[0],res[1])
    #a=crit.fonc_crit_moyenne_quantile(res[0],res[1],quantile)


    
    res_ini=a[1]

    nom_scenario=os.path.basename(fichier)[:-9]
    repertoire=os.path.join(os.path.dirname(fichier),"Runs",str("Sc_"+nom_scenario))
    repertoire_dclm=os.path.join(repertoire,os.listdir(repertoire)[0])
    repertoire_dfrt=os.path.join(repertoire_dclm,[f for f in os.listdir(repertoire_dclm) if os.path.isdir(os.path.join(repertoire_dclm, f))][0])
    fic_dfrt=os.path.join(repertoire_dfrt,str(nom_scenario+".dfrt.xml"))
    fic_dclm=os.path.join(repertoire_dclm,str(nom_scenario+".dclm.xml"))
    chemin_crue10=["\""+chemin_crue_10+"\""]
    for element in os.listdir(repertoire_dclm):
        if element.endswith('.etu.xml'):
            nom_etu=element
    fic_rcal=glob.glob(os.path.join(repertoire_dfrt,'*.rcal.xml'))[0]
    
    fic_etu=os.path.join(repertoire_dclm,nom_etu)
    arg_crue=chemin_crue10[0]+" -r -i -g -c " + fic_etu+ " > log.txt"
    arg=chemin_crue10+["-r", "-i" ,"-g" ,"-c" ,fic_etu]
    with open("lanc_bat.bat","wb") as fic:
        fic.write("@echo off"+"\n")
        fic.write(arg_crue)
    fic1=os.path.basename(fic_rcal)
    resu=lbin.recuperation_donnees(fic1,repertoire_dfrt,nom_calcul2)
    lbin.ecriture_resultat(resu[0],resu[1],resu[2],nom_calcul2,dico_dist,resu[3],resu[5])

    t1=time.time()
    lance_exe(["lanc_bat.bat"])
    t2=time.time()
    print "temps de simulation",t2-t1
    nb_it=max(max(int(float(temps_alloue)/(t2-t1))-2,int(float(temps_alloue)/2)-2),1) # decision du nombre de simulations selon temps alloue
    print temps_alloue,"s ",nb_it, "iterations"
    
    res=crit.extraction_csv_comp(pk,le_mes,"test.csv",nom_cal,nom_ecart)
    a=crit.fonc_crit_moyenne_quad(res[0],res[1],ponderation)
    #a=crit.fonc_crit_moyenne_max(res[0],res[1])
    #a=crit.fonc_crit_moyenne_quantile(res[0],res[1],quantile)
    res_ini=a[1]
    print "resultat initial",a[0],a[1]
    
    Val_ini=float(a[1])
    Val_min=float(a[1])
    Val_liste=a[0]
    Param_min=list(Init_stricklers)
    deb_min=Init_debit
    #boucle des tests a effectuer
    fic=open("trajectoire_montecarlo.txt","w")
    for l in range(nb_it):
        new_strickler=modif.tirage_alea(Max_stricklers,Min_stricklers)
        #print (new_strickler[1],Max_stricklers[1],Min_stricklers[1])
        modif.change_strickler_loi(new_strickler,fic_dfrt,nom_loi)
        new_debit=modif.tirage_debit(Min_debit,Max_debit)
        modif.change_debit(new_debit,fic_dclm,nom_calcul,nom_cl)
        lance_exe(["lanc_bat.bat"])
        lbin.ecriture_resultat(resu[0],resu[1],resu[2],nom_calcul2,dico_dist,resu[3],resu[5])
        res=crit.extraction_csv_comp(pk,le_mes,"test.csv",nom_cal,nom_ecart)
            
        
        #a=crit.fonc_crit_moyenne_abs(res[0],res[1])
        a=crit.fonc_crit_moyenne_quad(res[0],res[1],ponderation)
        #a=crit.fonc_crit_moyenne_max(res[0],res[1])
        #a=crit.fonc_crit_moyenne_quantile(res[0],res[1],0.68)
        chaine="n_it : {}/{}, crit courant {},crit min {}".format(str(l),str(nb_it),str(round(a[1],2)),str(round(Val_min,2)) )
        fic.write(chaine+"\n")
        print chaine
        if (a[1]<Val_min):
            Val_min=a[1]
            Val_liste=a[0]
            Param_min=list(new_strickler)
            deb_min=new_debit
            
    fin=time.time()
    fic.close()
    
    #Ecriture ds fichiers de resultat

    modif.change_strickler_loi(Param_min,fichier,nom_loi)
    modif.change_debit(deb_min,fichier4,nom_calcul,nom_cl)

    lance_otfa(sExeOtfa,sArg)
    
    res=crit.extraction_csv_comp(pk,le_mes,fic_csv2,nom_cal,nom_ecart)
    #Choix de la fonction critere a appliquer
    #a=crit.fonc_crit_moyenne_abs(res[0],res[1])
    a=crit.fonc_crit_moyenne_quad(res[0],res[1],ponderation)
    #a=crit.fonc_crit_moyenne_max(res[0],res[1])
    #a=crit.fonc_crit_moyenne_quantile(res[0],res[1],quantile)

    
    
    fic=open("resultat_montecarlo.txt","w")
    chaine="""
    Resultat initial :{}
    Minimum : {}
    Resultats ligne par ligne : {}
    Temps : {} s
    Parametres correspondants :
    {}
    """.format(str(Val_ini),str(Val_min),str(Val_liste),str(int(fin-debut)),str(Param_min))
    fic.write(chaine)
    print "resultat",a[0],a[1]
    fic.close()

    with open('resultat_debit_montecarlo.csv', 'wb') as fich:
        writer = csv.writer(fich,delimiter=";")
        for l in range(len(deb_min[:,1])):
            writer.writerow(deb_min[l,:])  
                
    with open('resultat_stricklers_montecarlo.csv', 'wb') as fic:
        writer = csv.writer(fic,delimiter=";")
        writer.writerow(["nom loi","nv parametres","old parametres"])
        for l in range(len(Param_min)):
            writer.writerow([str(nom_loi[l]),str(Param_min[l]),str(Init_stricklers[l])])

    

#Fonction de voisinage du recuit simule qui à partir de param de Stricklers initiaux tire de nv param selon une amplitude
#Stricklers consideres comme des entiers
def modify(Param_courant,ampli,wmin,wmax,fichier,temperature,nb_iter,loi):
    newparam=list()
    num=nb_iter%2
    valnew=0
    for l in range(len(Param_courant)):
        #if (ampli2[l]>0):
        if (ampli[l]>0):
            valnew=random.randrange(int(Param_courant[l]-ampli[l]),math.ceil(Param_courant[l]+ampli[l]))
            valnew=min(valnew,wmax[l])
            valnew=max(valnew,wmin[l])
            newparam.append(round(valnew,0))
        else:
            newparam.append(round(Param_courant[l],0))
    modif.change_strickler_loi(newparam,fichier,loi)
    return newparam

#Fonction de voisinage du recuit simule qui à partir de param de débits initiaux tire de nv param selon une amplitude donnees
def modify_debit(Param_courant,ampli,wmin,wmax,fichier,nom_calcul,nom_cl):
    newparam=numpy.zeros(Param_courant.shape)
    valnew=0
    n=Param_courant.shape[0]
    m=Param_courant.shape[1]
    for l in range(n):
        for k in range(m):
            if (ampli[l,k]>0):
                valnew=random.random()*(2*ampli[l,k])+(Param_courant[l,k]-ampli[l,k])
                valnew=min(valnew,wmax[l,k])
                valnew=max(valnew,wmin[l,k])
                newparam[l,k]=valnew
            else:
                newparam[l,k]=Param_courant[l,k]
    modif.change_debit(newparam,fichier,nom_calcul,nom_cl)
    return newparam

#Fonction de voisinage du recuit simule qui à partir de param de Stricklers initiaux tire de nv param selon une amplitude
#Stricklers consideres comme des reels
def modify_continu(Param_courant,ampli,wmin,wmax,fichier,loi):
    newparam=list()
    valnew=0
    for l in range(len(Param_courant)):
        if (ampli[l]>0):
            valnew=random.random()*(2*ampli[l])+(Param_courant[l]-ampli[l])
            valnew=min(valnew,wmax[l])
            valnew=max(valnew,wmin[l])
            newparam.append(valnew)
        else:
            newparam.append(Param_courant[l])
    modif.change_strickler_loi(newparam,fichier,loi)
    return newparam

#recuit simule transitoire rapide
def Simulated_Annealing_trans_rapide(sExeOtfa,sArg,fichier,fichier2,fic_csv2,temps_alloue,fic_excel,verbosite,chemin_crue_10):
    
    
    #Procédure du recuit simule
    debut=time.time() # mesure du temps d'execution
    #Copie des fichier strickler  et cond de debit initiaux
    if(fichier!=fichier2):
        shutil.copyfile(fichier2,fichier)
    
    #initialisation fenetre stricklers ici valeurs ini + ou - 2
    #resultat=modif.init_strickler_fenetre(fichier,5)
    resultat=crit.import_Stricklers(fic_excel)
    Max_stricklers=resultat[3]
    Min_stricklers=resultat[2]
    Init_stricklers=resultat[1]
    nom_loi=resultat[0]

    resultat=crit.import_transitoire(fic_excel)
    dico_section=resultat[0]
    res_ref=resultat[1]
    dico_temps1=resultat[2]
    nom_cal=resultat[3]
    resultat=crit.import_chemin_trans(fic_excel)
    if(len(resultat)>5):
        type_crit=resultat[5]
    else:
        type_crit="q"
    dico_res_ref=res_ref
    modif.change_strickler_loi(Init_stricklers,fichier,nom_loi)
    
    lance_otfa(sExeOtfa,sArg)
    
    nom_scenario=os.path.basename(fichier)[:-9]
    repertoire=os.path.join(os.path.dirname(fichier),"Runs",str("Sc_"+nom_scenario))
    repertoire_dclm=os.path.join(repertoire,os.listdir(repertoire)[0])
    repertoire_dfrt=os.path.join(repertoire_dclm,[f for f in os.listdir(repertoire_dclm) if os.path.isdir(os.path.join(repertoire_dclm, f))][0])
    fic_dfrt=os.path.join(repertoire_dfrt,str(nom_scenario+".dfrt.xml"))
    fic_dclm=os.path.join(repertoire_dclm,str(nom_scenario+".dclm.xml"))
    chemin_crue10=["\""+chemin_crue_10+"\""]
    for element in os.listdir(repertoire_dclm):
        if element.endswith('.etu.xml'):
            nom_etu=element
    fic_rcal=glob.glob(os.path.join(repertoire_dfrt,'*.rcal.xml'))[0]   
    fic_etu=os.path.join(repertoire_dclm,nom_etu)
    arg_crue=chemin_crue10[0]+" -r -i -g -c " + fic_etu+ " > log.txt"
    arg=chemin_crue10+["-r", "-i" ,"-g" ,"-c" ,fic_etu]
    with open("lanc_bat.bat","wb") as fic:
        fic.write("@echo off"+"\n")
        fic.write(arg_crue)
    fic1=os.path.basename(fic_rcal)
    resu=lbin.recuperation_donnees_trans(fic1,repertoire_dfrt,"Z")
    resultat=lbin.ecriture_resultat_trans(resu[0],resu[1],resu[2],resu[3],resu[4],dico_section)
    dico_temps2=resultat[1]
    dico_res_cal=resultat[0]
    t1=time.time()
    lance_exe(["lanc_bat.bat"])
    a=lbin.resultat_crit_trans(dico_res_ref,dico_temps1,dico_res_cal,dico_temps2,nom_cal,dico_section,type_crit)
    t2=time.time()
    
    print "temps de simulation",t2-t1
    nb_it=max(int(float(temps_alloue)/(t2-t1))-2,1) # decision du nombre de simulations selon temps alloue
    print temps_alloue,"s ",nb_it, "iterations"
    
    res_ini=a[1]
    l_ini=a[2]
    print a
    res_mul=float(res_ini)
    
    
    #initialisation minimum 
    Val_min=sys.maxint# soit on prend une valeur arbitraire
    #Val_min=float(a[1]) # soit on initialise avec le minimum
    Val_ini=Val_min
    Val_courant=Val_ini
    Val_new=Val_ini
    Val_liste=list()
    Val_min_liste=list()
    Val_liste_courant=list()
    for i in range(len(a[0])):
        Val_liste.append(100000)
        Val_min_liste.append(100000)
        Val_liste_courant.append(100000)
    Param_min=list(Init_stricklers)
    Param_courant=list(Init_stricklers)
    Param_new=list(Init_stricklers)

    #bornes pour la fenetre des stricklers 
    wmax=numpy.array(Max_stricklers)
    wmin=numpy.array(Min_stricklers)
    sens=1 #1 si on minimise -1 si on maximise 
    nbvar = len(Init_stricklers) # nb variables stricklers consideree

    #initialisation de la température
    t0 = 0.5               
    temperature=t0
    tfinal=0.001
    dth=1.0-((tfinal*t0/temperature)**(1.0/(nb_it))) # facteur de decroissance de la temperature pour obtenir le nombre d iteration correspondant au temps alloue

    #amplitude maximale des modifs de consignes
    ampli0 = 0.5*(wmax-wmin)
    ampli = ampli0
    nb_iter = 0                     #nombre d'itérations du recuit
    ntot = 0
    nequil= 1 
    seuil_amelioration=0.00001 # seuil de tolerance pour amelioration du minimum
    Param_new= list(modify_continu(Param_courant,ampli,wmin,wmax,fic_dfrt,nom_loi)) # considerer stricklers comme reel et tronquer le resultat final
    lance_exe(["lanc_bat.bat"])
    resu=lbin.recuperation_donnees_trans(fic1,repertoire_dfrt,"Z")
    resultat=lbin.ecriture_resultat_trans(resu[0],resu[1],resu[2],resu[3],resu[4],dico_section)
    dico_res_cal=resultat[0]
    a=lbin.resultat_crit_trans(dico_res_ref,dico_temps1,dico_res_cal,dico_temps2,nom_cal,dico_section,type_crit)

    mul=1.0
    while(abs(res_mul*mul)<1.0 or abs(a[1]-res_ini)*mul<1.0):
        mul=mul*10.0
    print "resultat initial",abs(res_ini),l_ini
    Val_new = float(a[1])*mul
    chaine="Simulations pour l'algorithme du Recuit Simulé"
    print chaine


    # definition variables locales
    with open("trajectoire_recuit.txt","w") as fic_traj: 
        
        
        
        #boucle sur la température
        while (temperature/t0 >tfinal and nb_iter<nb_it):
            idem = 0
            #changement de l amplitude selon la temperature
            ampli = ampli0*temperature / t0
            #ampli= numpy.where(ampli<1,1,ampli)
            test=0.0
            rdom=0.

            #modification aléatoire des consignes et nouvelle évaluation de la fonction-coût
            Param_new= list(modify_continu(Param_courant,ampli,wmin,wmax,fic_dfrt,nom_loi)) # considerer stricklers comme reel et tronquer le resultat final

            lance_exe(["lanc_bat.bat"])
            resu=lbin.recuperation_donnees_trans(fic1,repertoire_dfrt,"Z")
            resultat=lbin.ecriture_resultat_trans(resu[0],resu[1],resu[2],resu[3],resu[4],dico_section)
            dico_res_cal=resultat[0]
            a=lbin.resultat_crit_trans(dico_res_ref,dico_temps1,dico_res_cal,dico_temps2,nom_cal,dico_section,type_crit)
            Val_new = float(a[1])*mul
            Val_liste=a[2]

            #cas ou l optimum est ameliore
            if (sens*(Val_new-Val_min) < seuil_amelioration): 
                Val_min = Val_new
                Param_min =list(Param_new)     #mise à jour de l'optimum
                Val_courant = Val_new
                Param_courant=list(Param_new)      #on garde la nouvelle consigne

            #cas ou fonction meilleure que la precedente
            elif (sens*(Val_new-Val_courant) < seuil_amelioration):  
                Val_courant = Val_new
                Param_courant=list(Param_new)

            #cas ou nouvelle solution moins bonne que la precedente
            else:
                test = math.exp(-sens*(Val_new-Val_min)/temperature)
                #tirage aléatoire
                rdom=random.random()
            if (test > rdom):  #>>>on garde la nouvelle consigne
                Val_courant = Val_new
                Param_courant=list(Param_new)
         
            print a[2]        
            nb_iter=nb_iter+1
            chaine="n : {}/{}, temp : {}, ampli : {}, new : {}, cour : {}, min : {}".format(nb_iter,nb_it,round(temperature/t0,2),round(numpy.max(ampli),2),round(Val_new,4),round(Val_courant,4),round(Val_min,4))
            print(chaine)
            
            fic_traj.write(str(chaine+"\n"))
            fic_traj.flush()

            temperature = temperature*(1.0 -dth)
            
        #test avec parametres optimaux entiers trouves
        ampli=0.0*ampli # pour tronquer parametre en entiers
        #Param_new= list(modify(Param_min,ampli,wmin,wmax,fic_dfrt,temperature,nb_iter,nom_loi)) #nouveaux parametres optimaux
        Param_new=list(modify_continu(Param_min,ampli,wmin,wmax,fic_dfrt,nom_loi))
        #evaluation fonction critere
        lance_exe(["lanc_bat.bat"])
        resu=lbin.recuperation_donnees_trans(fic1,repertoire_dfrt,"Z")
        resultat=lbin.ecriture_resultat_trans(resu[0],resu[1],resu[2],resu[3],resu[4],dico_section)
        dico_res_cal=resultat[0]
        a=lbin.resultat_crit_trans(dico_res_ref,dico_temps1,dico_res_cal,dico_temps2,nom_cal,dico_section,type_crit)

        print "resultat",a[2],abs(a[1])
        Val_new = float(a[1])*mul
        Val_liste=a[2]
        fin=time.time()
        chaine="Resultat initial : {} Minimum : {} Minimum final : {}  Resultats crue par crue : {} ".format(str(res_ini),str(Val_min),str(a[1]),str(a[2]))
        fic_traj.write(chaine)
        fic_traj.flush()
    #fichier de resultat
    if(verbosite):
        fic=open("resultat_recuit_trans.txt","w")       
        chaine="Resultat initial {} \n {} \n Minimum {} \n Minimum final {} \n Resultats ligne par ligne {} \n Temps {} s \n Parametres correspondants : \n Strickler :\n {} \n ".format(str(res_ini),str(l_ini),str(Val_min),str(a[1]),str(a[2]),str(int(fin-debut)),Param_new)
        fic.write(chaine)
        a=lbin.resultat_crit_trans(dico_res_ref,dico_temps1,dico_res_cal,dico_temps2,nom_cal,dico_section,"v")
        chaine="resultat en difference de volume \n {} \n {} \n".format(str(a[1]),str(a[2]))
        fic.write(chaine)
        a=lbin.resultat_crit_trans(dico_res_ref,dico_temps1,dico_res_cal,dico_temps2,nom_cal,dico_section,"h")
        chaine="resultat en  difference de pic \n {} \n {} \n".format(str(a[1]),str(a[2]))
        fic.write(chaine)
        a=lbin.resultat_crit_trans(dico_res_ref,dico_temps1,dico_res_cal,dico_temps2,nom_cal,dico_section,"q")
        chaine="resultat en difference d ecart quadratique \n {} \n {} \n".format(str(a[1]),str(a[2]))
        fic.write(chaine)
        fic.close()
        
        with open('resultat_stricklers_trans.csv', 'wb') as fic:
            writer = csv.writer(fic,delimiter=";")
            writer.writerow(["nom loi","nv parametres","old parametres"])
            for l in range(len(Param_new)):
                writer.writerow([str(nom_loi[l]),str(Param_new[l]),str(Init_stricklers[l])])
    return Param_new,a[1],Init_stricklers

def analyse_sensibilite(sExeOtfa,sArg,fichier,fichier2,fichier3,fichier4,fic_csv2,temps_alloue,ifdebit,fic_excel,verbosite,if_not_reprise,debit_ini,chemin_crue_10):
    resultat=crit.import_le_mesure(fic_excel)
    le_mes=resultat[1]
    pk=resultat[0]
    ponderation=list()
    for i in range(len(le_mes[1,:])):
        ponderation.append(0)
    liste_critere_min=list()
    liste_critere_max=list()
    for i in range(len(le_mes[1,:])):
        ponderation[i]=1.0
        nom_str="stricklers_mini_AS_LE"+str(i)+".csv"
        nom_cal="le_cal_mini_as_le"+str(i)+".csv"
        nom_ecart="ecart_mini_as_le"+str(i)+".csv"
        resu_min=Simulated_Annealing_AS(sExeOtfa,sArg,fichier,fichier2,fichier3,fichier4,fic_csv2,temps_alloue,ifdebit,fic_excel,ponderation,verbosite,if_not_reprise,debit_ini,chemin_crue_10,nom_str,True,nom_cal,nom_ecart)
        nom_str="stricklers_maxi_AS_LE"+str(i)+".csv"
        nom_cal="le_cal_maxi_as_le"+str(i)+".csv"
        nom_ecart="ecart_maxi_as_le"+str(i)+".csv"
        resu_max=Simulated_Annealing_AS(sExeOtfa,sArg,fichier,fichier2,fichier3,fichier4,fic_csv2,temps_alloue,ifdebit,fic_excel,ponderation,verbosite,if_not_reprise,debit_ini,chemin_crue_10,nom_str,False,nom_cal,nom_ecart)
        enveloppe_min=resu_min[1][:,i]
        liste_critere_min.append(resu_min[3])
        liste_critere_max.append(resu_max[3])
        distance=resu_min[2]
        res_ref=resu_min[0][:,i]
        enveloppe_max=resu_max[1][:,i]
        maxi=max(numpy.max(enveloppe_max),numpy.max(res_ref[res_ref>0]))
        mini=min(numpy.min(enveloppe_min[enveloppe_min>0]),numpy.min(res_ref[res_ref>0]))
        plt.figure()
        plt.plot(distance,res_ref,"k+",label="mesures")
        plt.plot(distance,enveloppe_max,"r",label="enveloppe max")
        plt.plot(distance,enveloppe_min,"b",label="enveloppe min")
        plt.xlabel("PK")
        plt.ylabel("cote")
        plt.grid(True)
        plt.ylim((mini,maxi))
        plt.title("AS_ligne_eau")
        plt.legend()
        nom_fig="AS_ligne_eau_"+str(i)+".png"
        plt.savefig(nom_fig,format="png")
        plt.show(block=False)
        plt.close()
        ponderation[i]=0
    with open("resultat_as.txt","wb") as fic:
        fic.write("Liste des moyennes des enveloppes min\n")
        for i in range(len(le_mes[1,:])):
                  fic.write(str(round(liste_critere_min[i],2))+" ")
        fic.write("\nListe des moyennes des enveloppes max\n")
        for i in range(len(le_mes[1,:])):
                  fic.write(str(round(liste_critere_max[i],2))+" ")
        
#procedure du recuit simule
def Simulated_Annealing_AS(sExeOtfa,sArg,fichier,fichier2,fichier3,fichier4,fic_csv2,temps_alloue,ifdebit,fic_excel,ponderation,verbosite,if_not_reprise,debit_ini,chemin_crue_10,nom_str,boolmin,nom_cal,nom_ecart):
    
    
    #Procédure du recuit simule
    debut=time.time() # mesure du temps d'execution
    #Copie des fichier strickler  et cond de debit initiaux
    if(if_not_reprise):
        if(fichier2!=fichier):
            shutil.copyfile(fichier2,fichier)
        if(fichier3!=fichier4):
            shutil.copyfile(fichier3,fichier4)
    
    #initialisation fenetre stricklers ici valeurs ini + ou - 2
    #resultat=modif.init_strickler_fenetre(fichier,5)
    resultat=crit.import_Stricklers(fic_excel)
    Max_stricklers=resultat[3]
    Min_stricklers=resultat[2]
    Init_stricklers=resultat[1]
    nom_loi=resultat[0]
    resultat=crit.import_le_mesure(fic_excel)
    le_mes=resultat[1]
    pk=resultat[0]
    #Min_Maj_stricklers=resultat[3]
    #initialisation fenetre des debits
    if (ifdebit):
        resultat=crit.import_debit(fic_excel)
        nom_calcul=modif.lire_calcul(fic_csv2)
        #extraction de "CC_Pxx"
        nom_calcul2=list(nom_calcul)
        for l in range(len(nom_calcul2)):
            nom_calcul2[l]=nom_calcul2[l][4:]
        nom_cl=resultat[3]
        #resultat=modif.initial_debit(fichier4,nom_calcul,nom_cl)
        Max_debit=resultat[2]
        Min_debit=resultat[1]
        if(if_not_reprise):
            Init_debit=resultat[0]
        else:
            Init_debit=debit_ini

    # test parametres initiaux
    if(if_not_reprise):
        modif.change_strickler_loi(Init_stricklers,fichier,nom_loi)
        if(ifdebit):
           modif.change_debit(Init_debit,fichier4,nom_calcul,nom_cl)
        lance_otfa(sExeOtfa,sArg)
    #res=crit.extraction_csv(fic_csv1,fic_csv2)
    res=crit.extraction_csv_comp(pk,le_mes,fic_csv2,nom_cal,nom_ecart)
    dico_dist=res[4]
    #Choix de la fonction critere a appliquer
    #a=crit.fonc_crit_moyenne_abs(res[0],res[1])
    a=crit.fonc_crit_ecart_ref_cal(res[0],res[1],ponderation)
    #a=crit.fonc_crit_moyenne_max(res[0],res[1])
    #a=crit.fonc_crit_moyenne_quantile(res[0],res[1],quantile)
    res_ini=a[1]
    
    
    nom_scenario=os.path.basename(fichier)[:-9]
    repertoire=os.path.join(os.path.dirname(fichier),"Runs",str("Sc_"+nom_scenario))
    #print repertoire
    #print glob.glob(repertoire+"\\*.*")
    repertoire_dclm=os.path.join(repertoire,os.listdir(repertoire)[0])
    repertoire_dfrt=os.path.join(repertoire_dclm,[f for f in os.listdir(repertoire_dclm) if os.path.isdir(os.path.join(repertoire_dclm, f))][0])
    fic_dfrt=os.path.join(repertoire_dfrt,str(nom_scenario+".dfrt.xml"))
    fic_dclm=os.path.join(repertoire_dclm,str(nom_scenario+".dclm.xml"))
    chemin_crue10=["\""+chemin_crue_10+"\""]
    for element in os.listdir(repertoire_dclm):
        if element.endswith('.etu.xml'):
            nom_etu=element
    fic_rcal=glob.glob(os.path.join(repertoire_dfrt,'*.rcal.xml'))[0]
    
    fic_etu=os.path.join(repertoire_dclm,nom_etu)
    arg_crue=chemin_crue10[0]+" -r -i -g -c " + fic_etu+ " > log.txt"
    arg=chemin_crue10+["-r", "-i" ,"-g" ,"-c" ,fic_etu]
    with open("lanc_bat.bat","wb") as fic:
        fic.write("@echo off"+"\n")
        fic.write(arg_crue)
    fic1=os.path.basename(fic_rcal)
    resu=lbin.recuperation_donnees(fic1,repertoire_dfrt,nom_calcul2)
    lbin.ecriture_resultat(resu[0],resu[1],resu[2],nom_calcul2,dico_dist,resu[3],resu[5])

    t1=time.time()
    lance_exe(["lanc_bat.bat"])
    res=crit.extraction_csv_comp(pk,le_mes,"test.csv",nom_cal,nom_ecart)
    a=crit.fonc_crit_ecart_ref_cal(res[0],res[1],ponderation)
    t2=time.time()
    print "temps de simulation",t2-t1
    nb_it=max(max(int(float(temps_alloue)/(t2-t1))-2,int(float(temps_alloue)/2)-2),1) # decision du nombre de simulations selon temps alloue
    print temps_alloue,"s ",nb_it, "iterations"
    
    #a=crit.fonc_crit_moyenne_max(res[0],res[1])
    #a=crit.fonc_crit_moyenne_quantile(res[0],res[1],quantile)
    res_ini=a[1]
    print "resultat initial",a[0],a[1]


    #initialisation minimum
    if(boolmin):
        Val_min=100000
    else:
        Val_min=0# soit on prend une valeur arbitraire
    #Val_min=float(a[1]) # soit on initialise avec le minimum
    Val_ini=Val_min
    Val_courant=Val_ini
    Val_new=Val_ini
    Val_liste=list()
    Val_min_liste=list()
    Val_liste_courant=list()
    for i in range(len(a[0])):
        if ponderation[i]>0:
            Val_liste.append(100000)
            Val_min_liste.append(100000)
            Val_liste_courant.append(100000)
        else:
            Val_liste.append(a[0][i])
            Val_min_liste.append(a[0][i])
            Val_liste_courant.append(a[0][i]) 
    Param_min=list(Init_stricklers)
    Param_courant=list(Init_stricklers)
    Param_new=list(Init_stricklers)

    if(ifdebit):
        deb_min=numpy.array(Init_debit)
        deb_courant=numpy.array(Init_debit)
        deb_new=numpy.array(Init_debit)
        
    #bornes pour la fenetre des stricklers 
    wmax=numpy.array(Max_stricklers)
    wmin=numpy.array(Min_stricklers)

    
    chaine="Simulations pour l'algorithme du Recuit Simulé"
    print chaine


    # definition variables locales
    with open("trajectoire_recuit.txt","w") as fic_traj:
        if(boolmin):
            sens=1 #1 si on minimise -1 si on maximise
        else :
            sens=-1.0
        nbvar = len(Init_stricklers) # nb variables stricklers consideree

        #initialisation de la température
        t0 = 0.5               
        temperature=t0
        tfinal=0.005
        dth=1.0-((tfinal*t0/temperature)**(1.0/(nb_it))) # facteur de decroissance de la temperature pour obtenir le nombre d iteration correspondant au temps alloue

        #amplitude maximale des modifs de consignes
        if(if_not_reprise):
            ampli0 = 0.5*(wmax-wmin)
            ampli = ampli0
        else:
            ampli0 = 0.5*(wmax-wmin)
            ampli0=ampli0*0.0
            ampli=ampli0
        if(ifdebit):
            ampli_deb0=0.5*(Max_debit-Min_debit)
            ampli_deb=ampli_deb0
            for l in range(len(ponderation)):
                if(ponderation[l]==0):
                    ampli_deb0[:,l]=ampli_deb0[:,l]*0.0
                    ampli_deb[:,l]=0.0*ampli_deb[:,l]
        nb_iter = 0                     #nombre d'itérations du recuit
        ntot = 0
        nequil= 1 
        seuil_amelioration=0.0001 # seuil de tolerance pour amelioration du minimum
        
        
        #boucle sur la température
        while (temperature/t0 >tfinal and nb_iter<nb_it):
            idem = 0
            #changement de l amplitude selon la temperature
            ampli = ampli0*temperature / t0
            if(ifdebit):
                ampli_deb=ampli_deb0*temperature / t0
            #ampli= numpy.where(ampli<1,1,ampli)
            test=0.0
            rdom=0.

            #modification aléatoire des consignes et nouvelle évaluation de la fonction-coût
            #Param_new= list(modify(Param_courant,ampli,wmin,wmax,fichier,temperature, Min_Maj_stricklers)) # considerer les stricklers comme entiers
            if(if_not_reprise):
                Param_new= list(modify_continu(Param_courant,ampli,wmin,wmax,fic_dfrt,nom_loi)) # considerer stricklers comme reel et tronquer le resultat final

            #changement du debit ici considere comme reel 
            if(ifdebit):
                deb_new=modify_debit(deb_courant,ampli_deb,Min_debit,Max_debit,fic_dclm,nom_calcul,nom_cl)
            #evcaluation de la fonction critere
            #lance_otfa(chemin_crue10,arg_crue)
            #lance_exe(arg)
            lance_exe(["lanc_bat.bat"])
            #resu=lbin.recuperation_donnees(os.path.basename(fic_rcal),repertoire_dfrt,nom_calcul2)
            lbin.ecriture_resultat(resu[0],resu[1],resu[2],nom_calcul2,dico_dist,resu[3],resu[5])
            #lbin.ecriture_resultat(resu[0],resu[1],resu[2],nom_calcul2,dico_dist)
            #res=crit.extraction_csv(fic_csv1,fic_csv2)
            res=crit.extraction_csv_comp(pk,le_mes,"test.csv",nom_cal,nom_ecart)
            #res=crit.extraction_csv_comp(pk,le_mes,fic_csv2)
            #a=crit.fonc_crit_moyenne_abs(res[0],res[1])
            a=crit.fonc_crit_ecart_ref_cal(res[0],res[1],ponderation)
            #a=crit.fonc_crit_moyenne_max(res[0],res[1])
            #a=crit.fonc_crit_moyenne_quantile(res[0],res[1],quantile)  
            Val_new = float(a[1])
            Val_liste=a[0]
            if( not if_not_reprise):
                for l in range(len(a[0])):
                    if ponderation[l]>0:
                        if (sens*(Val_liste[l]-Val_min_liste[l]) < seuil_amelioration): 
                            Val_min_liste[l] = Val_liste[l]
                            Val_min = Val_new
                            Val_courant = Val_new
                            Val_liste_courant[l] = Val_liste[l]
                            if(ifdebit):
                                deb_courant[:,l]=copy.deepcopy(deb_new[:,l])
                                deb_min[:,l]=copy.deepcopy(deb_new[:,l])

                        #cas ou fonction meilleure que la precedente
                        elif (sens*(Val_liste[l]-Val_liste_courant[l]) < seuil_amelioration):  
                            Val_liste_courant[l] = Val_liste[l]
                            Val_courant = Val_new
                            if(ifdebit):
                                deb_courant[:,l]=copy.deepcopy(deb_new[:,l])

                        #cas ou nouvelle solution moins bonne que la precedente
                        else:
                            test = math.exp(-sens*(Val_liste[l]-Val_min_liste[l])/temperature)
                            #tirage aléatoire
                            rdom=random.random()
                            if (test > rdom):  #>>>on garde la nouvelle consigne
                                Val_liste_courant[l] = Val_liste[l]
                                Val_courant = Val_new
                                #tests pour savoir si on garde ou non la nouvelle consigne
                                if(ifdebit):
                                    deb_courant[:,l]=copy.deepcopy(deb_new[:,l])
                affiche=list()
                for k in range(len(Val_min_liste)):
                    affiche.append(round(Val_min_liste[k],2))
                print affiche
            else:
                
                #cas ou l optimum est ameliore
                if (sens*(Val_new-Val_min) < seuil_amelioration): 
                    Val_min = Val_new
                    Param_min =list(Param_new)     #mise à jour de l'optimum
                    Val_courant = Val_new
                    if(ifdebit):
                        deb_courant=numpy.array(deb_new)
                        deb_min=numpy.array(deb_new)
                    Param_courant=list(Param_new)      #on garde la nouvelle consigne

                #cas ou fonction meilleure que la precedente
                elif (sens*(Val_new-Val_courant) < seuil_amelioration):  
                    Val_courant = Val_new
                    if(ifdebit):
                        deb_courant=numpy.array(deb_new)
                    Param_courant=list(Param_new)

                #cas ou nouvelle solution moins bonne que la precedente
                else:
                    test = math.exp(-sens*(Val_new-Val_min)/temperature)
                    #tirage aléatoire
                    rdom=random.random()
                if (test > rdom):  #>>>on garde la nouvelle consigne
                    Val_courant = Val_new
                    if(ifdebit):
                        deb_courant=numpy.array(deb_new)
                    Param_courant=list(Param_new)
             
            print a[0]        
            nb_iter=nb_iter+1
            chaine="n : {}/{}, temp : {}, ampli : {}, {}, new : {}, cour : {}, min : {}".format(nb_iter,nb_it,round(temperature/t0,2),round(numpy.max(ampli),2),round(numpy.max(ampli_deb),2),round(Val_new,2),round(Val_courant,2),round(Val_min,2))
            print(chaine)
            fic_traj.write(str(chaine+"\n"))
            fic_traj.flush()

            temperature = temperature*(1.0 -dth)
            
        #test avec parametres optimaux entiers trouves
        ampli=0.0*ampli # pour tronquer parametre en entiers
        ampli_deb=ampli_deb*0.0
        if (ifdebit):
            deb_new=numpy.array(deb_min)
            modify_debit(deb_new,ampli_deb,Min_debit,Max_debit,fic_dclm,nom_calcul,nom_cl)
        if(if_not_reprise):
            Param_new= list(modify(Param_min,ampli,wmin,wmax,fic_dfrt,temperature,nb_iter,nom_loi)) #nouveaux parametres optimaux
        #evaluation fonction critere
        lance_exe(["lanc_bat.bat"])
        #lance_exe(arg)
        #resu=lbin.recuperation_donnees(os.path.basename(fic_rcal),repertoire_dfrt,nom_calcul2)
        #lbin.ecriture_resultat(resu[0],resu[1],resu[2],nom_calcul2,dico_dist)
        lbin.ecriture_resultat(resu[0],resu[1],resu[2],nom_calcul2,dico_dist,resu[3],resu[5])
        #res=crit.extraction_csv(fic_csv1,fic_csv2)
        res=crit.extraction_csv_comp(pk,le_mes,"test.csv",nom_cal,nom_ecart)
        #a=crit.fonc_crit_moyenne_abs(res[0],res[1])
        a=crit.fonc_crit_ecart_ref_cal(res[0],res[1],ponderation)
        #a=crit.fonc_crit_moyenne_max(res[0],res[1])
        #a=crit.fonc_crit_moyenne_quantile(res[0],res[1],quantile)
        fin=time.time()
        chaine="Resultat initial : {} Minimum : {} Minimum final : {}  Resultats ligne par ligne : {} ".format(str(res_ini),str(Val_min),str(a[1]),str(a[0]))
        fic_traj.write(chaine)
        fic_traj.flush()
    #fichier de resultat
    if (if_not_reprise):
        with open(nom_str, 'wb') as fic:
            writer = csv.writer(fic,delimiter=";")
            writer.writerow(["nom loi","nv parametres","old parametres"])
            for l in range(len(Param_new)):
                writer.writerow([str(nom_loi[l]),str(Param_new[l]),str(Init_stricklers[l])])
    print "resultat",a[1]/100,a[0]

    return res[0],res[2],res[3],a[1]/100


#procedure du recuit simule
def Simulated_Annealing(sExeOtfa,sArg,fichier,fichier2,fichier3,fichier4,fic_csv2,temps_alloue,ifdebit,fic_excel,ponderation,verbosite,if_not_reprise,debit_ini,chemin_crue_10,nom_str,nom_cal,nom_ecart):
    
    
    #Procédure du recuit simule
    debut=time.time() # mesure du temps d'execution
    #Copie des fichier strickler  et cond de debit initiaux
    if(if_not_reprise):
        if(fichier2!=fichier):
            shutil.copyfile(fichier2,fichier)
        if(fichier3!=fichier4):
            shutil.copyfile(fichier3,fichier4)
    
    #initialisation fenetre stricklers ici valeurs ini + ou - 2
    #resultat=modif.init_strickler_fenetre(fichier,5)
    resultat=crit.import_Stricklers(fic_excel)
    Max_stricklers=resultat[3]
    Min_stricklers=resultat[2]
    Init_stricklers=resultat[1]
    nom_loi=resultat[0]
    resultat=crit.import_le_mesure(fic_excel)
    le_mes=resultat[1]
    pk=resultat[0]
    #Min_Maj_stricklers=resultat[3]
    #initialisation fenetre des debits
    if (ifdebit):
        resultat=crit.import_debit(fic_excel)
        nom_calcul=modif.lire_calcul(fic_csv2)
        #extraction de "CC_Pxx"
        nom_calcul2=list(nom_calcul)
        for l in range(len(nom_calcul2)):
            nom_calcul2[l]=nom_calcul2[l][4:]
        nom_cl=resultat[3]
        #resultat=modif.initial_debit(fichier4,nom_calcul,nom_cl)
        Max_debit=resultat[2]
        Min_debit=resultat[1]
        if(if_not_reprise):
            Init_debit=resultat[0]
        else:
            Init_debit=debit_ini

    # test parametres initiaux
    if(if_not_reprise):
        modif.change_strickler_loi(Init_stricklers,fichier,nom_loi)
        if(ifdebit):
           modif.change_debit(Init_debit,fichier4,nom_calcul,nom_cl)
        lance_otfa(sExeOtfa,sArg)
    #res=crit.extraction_csv(fic_csv1,fic_csv2)
    res=crit.extraction_csv_comp(pk,le_mes,fic_csv2,nom_cal,nom_ecart)
    dico_dist=res[4]
    #Choix de la fonction critere a appliquer
    #a=crit.fonc_crit_moyenne_abs(res[0],res[1])
    a=crit.fonc_crit_moyenne_quad(res[0],res[1],ponderation)
    #a=crit.fonc_crit_moyenne_max(res[0],res[1])
    #a=crit.fonc_crit_moyenne_quantile(res[0],res[1],quantile)
    res_ini=a[1]
    
    
    nom_scenario=os.path.basename(fichier)[:-9]
    repertoire=os.path.join(os.path.dirname(fichier),"Runs",str("Sc_"+nom_scenario))
    #print repertoire
    #print glob.glob(repertoire+"\\*.*")
    repertoire_dclm=os.path.join(repertoire,os.listdir(repertoire)[0])
    repertoire_dfrt=os.path.join(repertoire_dclm,[f for f in os.listdir(repertoire_dclm) if os.path.isdir(os.path.join(repertoire_dclm, f))][0])
    fic_dfrt=os.path.join(repertoire_dfrt,str(nom_scenario+".dfrt.xml"))
    fic_dclm=os.path.join(repertoire_dclm,str(nom_scenario+".dclm.xml"))
    chemin_crue10=["\""+chemin_crue_10+"\""]
    for element in os.listdir(repertoire_dclm):
        if element.endswith('.etu.xml'):
            nom_etu=element
    fic_rcal=glob.glob(os.path.join(repertoire_dfrt,'*.rcal.xml'))[0]
    
    fic_etu=os.path.join(repertoire_dclm,nom_etu)
    arg_crue=chemin_crue10[0]+" -r -i -g -c " + fic_etu+ " > log.txt"
    arg=chemin_crue10+["-r", "-i" ,"-g" ,"-c" ,fic_etu]
    with open("lanc_bat.bat","wb") as fic:
        fic.write("@echo off"+"\n")
        fic.write(arg_crue)
    fic1=os.path.basename(fic_rcal)
    resu=lbin.recuperation_donnees(fic1,repertoire_dfrt,nom_calcul2)
    lbin.ecriture_resultat(resu[0],resu[1],resu[2],nom_calcul2,dico_dist,resu[3],resu[5])

    t1=time.time()
    lance_exe(["lanc_bat.bat"])
    res=crit.extraction_csv_comp(pk,le_mes,"test.csv",nom_cal,nom_ecart)
    a=crit.fonc_crit_moyenne_quad(res[0],res[1],ponderation)
    t2=time.time()
    nb_it=max(int(float(temps_alloue)/(t2-t1))-2,1) # decision du nombre de simulations selon temps alloue
    print "temps de simulation",t2-t1
    print temps_alloue,"s ",nb_it, "iterations"
    #a=crit.fonc_crit_moyenne_max(res[0],res[1])
    #a=crit.fonc_crit_moyenne_quantile(res[0],res[1],quantile)
    res_ini=a[1]
    print "resultat initial",a[0],a[1]


    #initialisation minimum 
    Val_min=100000.0 # soit on prend une valeur arbitraire
    #Val_min=float(a[1]) # soit on initialise avec le minimum
    Val_ini=Val_min
    Val_courant=Val_ini
    Val_new=Val_ini
    Val_liste=list()
    Val_min_liste=list()
    Val_liste_courant=list()
    for i in range(len(a[0])):
        if ponderation[i]>0:
            Val_liste.append(100000)
            Val_min_liste.append(100000)
            Val_liste_courant.append(100000)
        else:
            Val_liste.append(a[0][i])
            Val_min_liste.append(a[0][i])
            Val_liste_courant.append(a[0][i]) 
    Param_min=list(Init_stricklers)
    Param_courant=list(Init_stricklers)
    Param_new=list(Init_stricklers)

    if(ifdebit):
        deb_min=numpy.array(Init_debit)
        deb_courant=numpy.array(Init_debit)
        deb_new=numpy.array(Init_debit)
        
    #bornes pour la fenetre des stricklers 
    wmax=numpy.array(Max_stricklers)
    wmin=numpy.array(Min_stricklers)

    
    chaine="Simulations pour l'algorithme du Recuit Simulé"
    print chaine


    # definition variables locales
    with open("trajectoire_recuit.txt","w") as fic_traj: 
        sens=1 #1 si on minimise -1 si on maximise 
        nbvar = len(Init_stricklers) # nb variables stricklers consideree

        #initialisation de la température
        t0 = 0.5               
        temperature=t0
        tfinal=0.001
        dth=1.0-((tfinal*t0/temperature)**(1.0/(nb_it))) # facteur de decroissance de la temperature pour obtenir le nombre d iteration correspondant au temps alloue

        #amplitude maximale des modifs de consignes
        if(if_not_reprise):
            ampli0 = 0.5*(wmax-wmin)
            ampli = ampli0
        else:
            ampli0 = 0.5*(wmax-wmin)
            ampli0=ampli0*0.0
            ampli=ampli0
        if(ifdebit):
            ampli_deb0=0.5*(Max_debit-Min_debit)
            ampli_deb=ampli_deb0
            for l in range(len(ponderation)):
                if(ponderation[l]==0):
                    ampli_deb0[:,l]=ampli_deb0[:,l]*0.0
                    ampli_deb[:,l]=0.0*ampli_deb[:,l]
        nb_iter = 0                     #nombre d'itérations du recuit
        ntot = 0
        nequil= 1 
        seuil_amelioration=0.0001 # seuil de tolerance pour amelioration du minimum
        
        
        #boucle sur la température
        while (temperature/t0 >tfinal and nb_iter<nb_it):
            idem = 0
            #changement de l amplitude selon la temperature
            ampli = ampli0*temperature / t0
            if(ifdebit):
                ampli_deb=ampli_deb0*temperature / t0
            #ampli= numpy.where(ampli<1,1,ampli)
            test=0.0
            rdom=0.

            #modification aléatoire des consignes et nouvelle évaluation de la fonction-coût
            #Param_new= list(modify(Param_courant,ampli,wmin,wmax,fichier,temperature, Min_Maj_stricklers)) # considerer les stricklers comme entiers
            if(if_not_reprise):
                Param_new= list(modify_continu(Param_courant,ampli,wmin,wmax,fic_dfrt,nom_loi)) # considerer stricklers comme reel et tronquer le resultat final

            #changement du debit ici considere comme reel 
            if(ifdebit):
                deb_new=modify_debit(deb_courant,ampli_deb,Min_debit,Max_debit,fic_dclm,nom_calcul,nom_cl)
            #evcaluation de la fonction critere
            #lance_otfa(chemin_crue10,arg_crue)
            #lance_exe(arg)
            lance_exe(["lanc_bat.bat"])
            #resu=lbin.recuperation_donnees(os.path.basename(fic_rcal),repertoire_dfrt,nom_calcul2)
            lbin.ecriture_resultat(resu[0],resu[1],resu[2],nom_calcul2,dico_dist,resu[3],resu[5])
            #lbin.ecriture_resultat(resu[0],resu[1],resu[2],nom_calcul2,dico_dist)
            #res=crit.extraction_csv(fic_csv1,fic_csv2)
            res=crit.extraction_csv_comp(pk,le_mes,"test.csv",nom_cal,nom_ecart)
            #res=crit.extraction_csv_comp(pk,le_mes,fic_csv2)
            #a=crit.fonc_crit_moyenne_abs(res[0],res[1])
            a=crit.fonc_crit_moyenne_quad(res[0],res[1],ponderation)
            #a=crit.fonc_crit_moyenne_max(res[0],res[1])
            #a=crit.fonc_crit_moyenne_quantile(res[0],res[1],quantile)  
            Val_new = float(a[1])
            Val_liste=a[0]
            if( not if_not_reprise):
                for l in range(len(a[0])):
                    if ponderation[l]>0:
                        if (sens*(Val_liste[l]-Val_min_liste[l]) < seuil_amelioration): 
                            Val_min_liste[l] = Val_liste[l]
                            Val_min = Val_new
                            Val_courant = Val_new
                            Val_liste_courant[l] = Val_liste[l]
                            if(ifdebit):
                                deb_courant[:,l]=copy.deepcopy(deb_new[:,l])
                                deb_min[:,l]=copy.deepcopy(deb_new[:,l])

                        #cas ou fonction meilleure que la precedente
                        elif (sens*(Val_liste[l]-Val_liste_courant[l]) < seuil_amelioration):  
                            Val_liste_courant[l] = Val_liste[l]
                            Val_courant = Val_new
                            if(ifdebit):
                                deb_courant[:,l]=copy.deepcopy(deb_new[:,l])

                        #cas ou nouvelle solution moins bonne que la precedente
                        else:
                            test = math.exp(-sens*(Val_liste[l]-Val_min_liste[l])/temperature)
                            #tirage aléatoire
                            rdom=random.random()
                            if (test > rdom):  #>>>on garde la nouvelle consigne
                                Val_liste_courant[l] = Val_liste[l]
                                Val_courant = Val_new
                                #tests pour savoir si on garde ou non la nouvelle consigne
                                if(ifdebit):
                                    deb_courant[:,l]=copy.deepcopy(deb_new[:,l])
                affiche=list()
                for k in range(len(Val_min_liste)):
                    affiche.append(round(Val_min_liste[k],2))
                print affiche
            else:
                
                #cas ou l optimum est ameliore
                if (sens*(Val_new-Val_min) < seuil_amelioration): 
                    Val_min = Val_new
                    Param_min =list(Param_new)     #mise à jour de l'optimum
                    Val_courant = Val_new
                    if(ifdebit):
                        deb_courant=numpy.array(deb_new)
                        deb_min=numpy.array(deb_new)
                    Param_courant=list(Param_new)      #on garde la nouvelle consigne

                #cas ou fonction meilleure que la precedente
                elif (sens*(Val_new-Val_courant) < seuil_amelioration):  
                    Val_courant = Val_new
                    if(ifdebit):
                        deb_courant=numpy.array(deb_new)
                    Param_courant=list(Param_new)

                #cas ou nouvelle solution moins bonne que la precedente
                else:
                    test = math.exp(-sens*(Val_new-Val_min)/temperature)
                    #tirage aléatoire
                    rdom=random.random()
                if (test > rdom):  #>>>on garde la nouvelle consigne
                    Val_courant = Val_new
                    if(ifdebit):
                        deb_courant=numpy.array(deb_new)
                    Param_courant=list(Param_new)
             
                   
            nb_iter=nb_iter+1
            chaine="n : {}/{}, temp : {}, ampli : {}, {}, new : {}, cour : {}, min : {}".format(nb_iter,nb_it,round(temperature/t0,2),round(numpy.max(ampli),2),round(numpy.max(ampli_deb),2),round(Val_new,2),round(Val_courant,2),round(Val_min,2))
            if (nb_it<=5000):
                print a[0] 
                print(chaine)
            elif(nb_iter%10==0):
                print a[0] 
                print(chaine)
            fic_traj.write(str(chaine+"\n"))
            fic_traj.flush()

            temperature = temperature*(1.0 -dth)
            
        #test avec parametres optimaux entiers trouves
        ampli=0.0*ampli # pour tronquer parametre en entiers
        ampli_deb=ampli_deb*0.0
        if (ifdebit):
            deb_new=numpy.array(deb_min)
            modify_debit(deb_new,ampli_deb,Min_debit,Max_debit,fic_dclm,nom_calcul,nom_cl)
        if(if_not_reprise):
            Param_new= list(modify(Param_min,ampli,wmin,wmax,fic_dfrt,temperature,nb_iter,nom_loi)) #nouveaux parametres optimaux
        #evaluation fonction critere
        lance_exe(["lanc_bat.bat"])
        #lance_exe(arg)
        #resu=lbin.recuperation_donnees(os.path.basename(fic_rcal),repertoire_dfrt,nom_calcul2)
        #lbin.ecriture_resultat(resu[0],resu[1],resu[2],nom_calcul2,dico_dist)
        lbin.ecriture_resultat(resu[0],resu[1],resu[2],nom_calcul2,dico_dist,resu[3],resu[5])
        #res=crit.extraction_csv(fic_csv1,fic_csv2)
        res=crit.extraction_csv_comp(pk,le_mes,"test.csv",nom_cal,nom_ecart)
        #a=crit.fonc_crit_moyenne_abs(res[0],res[1])
        a=crit.fonc_crit_moyenne_quad(res[0],res[1],ponderation)
        #a=crit.fonc_crit_moyenne_max(res[0],res[1])
        #a=crit.fonc_crit_moyenne_quantile(res[0],res[1],quantile)
        if(verbosite):
             plot_le(res[3],res[3],res[0],res[2])
            #plot(res[0][:,1],res[1][:,1],"mes","cal","+","test","png")
            #temps de fin
        fin=time.time()
        chaine="Resultat initial : {} Minimum : {} Minimum final : {}  Resultats ligne par ligne : {} ".format(str(res_ini),str(Val_min),str(a[1]),str(a[0]))
        fic_traj.write(chaine)
        fic_traj.flush()
    #fichier de resultat
    if(verbosite):
        fic=open("resultat_recuit.txt","w")
        if (not(ifdebit)):
            deb_new="le debit n est pas pris en compte"
        else:
          with open('resultat_debit.csv', 'wb') as fich:
            writer = csv.writer(fich,delimiter=";")
            for l in range(len(deb_new[:,0])):
                writer.writerow(deb_new[l,:])  
                
        chaine="Resultat initial {} \n Minimum {} \n Minimum final {} \n Resultats ligne par ligne {} \n Temps {} s \n Parametres correspondants : \n Strickler :\n {} \n Debit : \n {}".format(str(res_ini),str(Val_min),str(a[1]),str(a[0]),str(int(fin-debut)),Param_new,deb_new)
        fic.write(chaine)
        fic.close()
    if (if_not_reprise):
        with open(nom_str, 'wb') as fic:
            writer = csv.writer(fic,delimiter=";")
            writer.writerow(["nom loi","nv parametres","old parametres"])
            for l in range(len(Param_new)):
                writer.writerow([str(nom_loi[l]),str(Param_new[l]),str(Init_stricklers[l])])
    print "resultat",a[1],a[0]
    return Param_new,deb_new,a[0],Init_stricklers

#fonction pour faire la liste de toutes les combinaisons possibles d une liste de liste
def listeproduit(L):
    if len(L)==0: # produit vide
        return [[]]
    else:
        K=listeproduit(L[1:]) #appel récursif 
        return [[x]+y for x in L[0] for y in K] #ajouter tous les éléments du premier ensemble au produit cartésien des autres
 
#fonction qui execute la methode de validation croisee pour selection la combinaison de choix de ligne d'eau optimale pour le critere retenu
def validation_croisee(sExeOtfa,fic_otfa,fichier_dfrt_cible,fichier_dfrt_ori,fic_dclm_ori,fic_dclm_cible,fic_csv_le_cal,temps_alloue,True,fic_excel,gamme_q,effectif,pond_val,chemin_crue_10):

    #evaluation des combinaisons de lignes d eau a tester
    with open('trajectoire_cv.txt','w') as fic:
        fic.write("\n")
        
    #remplissage dictionnaire effectif par gamme de debit
    dico_effectif=dict()
    for i in range(len(gamme_q)):
        dico_effectif[gamme_q[i]]=int(float(effectif[i]))
    ensemble_gamme=list(set(gamme_q))
    nb_gamme=len(ensemble_gamme)
    
    #remplissage dictionnaire correspondance nom ligne d eau gamme de debit
    dico_correspondance=dict()
    j=0
    nom_str='resultat_stricklers'
    while(j<nb_gamme):
        dummy=list()
        for i in range(len(gamme_q)):
            if(ensemble_gamme[j]==gamme_q[i]):
                dummy.append(i)
        dico_correspondance[ensemble_gamme[j]]=dummy
        j=j+1
        
    #remplissage liste combinaisons de ligne d eau a tester en apprentissage
    liste_combi=list()
    
    for i in range(nb_gamme):
        a=list()
        b=list(dico_correspondance[ensemble_gamme[i]])
        n_effec=dico_effectif[ensemble_gamme[i]]
        
        #combinaison des ensemble de lignes d eau par gamme de debit a neffec elements
        for p in itertools.combinations(b,n_effec):
            a.append(list(p))
        liste_combi.append(a)
        
    # calcul de la liste totale de combinaisons possibles
    liste_combi=listeproduit(liste_combi)
    liste_combi_finale=list()
    
    # affichage des combinaisons sous forme de liste( et non listes de listes)
    for k in range(len(liste_combi)):
        liste=list()
        for i in range(len(liste_combi[k])):
            for j in range(len(liste_combi[k][i])):
                liste.append(liste_combi[k][i][j])
        liste_combi_finale.append(liste)
    print liste_combi_finale
    a=range(len(gamme_q))
    
    print "nombre de combinaisons a tester",len(liste_combi_finale)
    print "temps estime",round(float(temps_alloue)*3/2.0*len(liste_combi_finale)/3600,1),"h"
        
    j=0
    
    #initialisation des erreurs mini et des parametres optimaux
    erreur_min=10000000.0
    err_tot=0.0
    print pond_val
    ponderation_min=list()
    Param_min=list()

    #bouvcle finale sur le nombre de combinaisons a tester 
    while (j<len(liste_combi_finale)):
        ponderation=numpy.zeros(len(gamme_q))
        nom_fic_str=nom_str+"_combi_"+str(j)+".csv"
        nom_cal="resultat_cal_combi_"+str(j)+".csv"
        nom_ecart="resultat_ecart_combi_"+str(j)+".csv"
        #remplissage de la ponderation relative a la combinaison en cours
        for i in range(len(liste_combi_finale[j])):
            ponderation[liste_combi_finale[j][i]]=1.0
            
        #affichage pour plus de clarte
        print ponderation,sorted(liste_combi_finale[j])
        
        #argument fantome pour que strickler changent dans le recuit simule
        dummy="dummy"
        
        #Recuit simule sur les lignes d eau correspondant a la ponderation choisie
        res=Simulated_Annealing(sExeOtfa,fic_otfa,fichier_dfrt_cible,fichier_dfrt_ori,fic_dclm_ori,fic_dclm_cible,fic_csv_le_cal,temps_alloue,True,fic_excel,ponderation,False,True,dummy,chemin_crue_10,nom_fic_str,nom_cal,nom_ecart)

        #initialisation erreurs
        erreur_apprentissage=0.0
        erreur_validation=0.0
        nb_pond=0
        
        #calcul de l erreur d apprentissage
        for i in range(len(ponderation)):
            if(ponderation[i]>0):
                nb_pond=nb_pond+1
                erreur_apprentissage=erreur_apprentissage+res[2][i]
            else:
                erreur_validation=erreur_validation+res[2][i]

        erreur_apprentissage=erreur_apprentissage/nb_pond
        
        #calcul de l erreur de validation
        if(nb_pond<len(ponderation)):
            erreur_validation=0.0
            pond=list(ponderation)
            #definition de la ponderation complementaire
            for eff_pond in range(len(effectif)):
                if(int(float(effectif[eff_pond]))>0):
                    pond[eff_pond]=1-ponderation[eff_pond]
                else:
                    pond[eff_pond]=0
                    
            print pond
            # recuit simule uniquement sur les debits des lignes  eau a valider avec debits issus du resultat precedent pour les lignes d eau d apprentissage 
            res1=Simulated_Annealing(sExeOtfa,fic_otfa,fichier_dfrt_cible,fichier_dfrt_ori,fic_dclm_ori,fic_dclm_cible,fic_csv_le_cal,str(float(temps_alloue)/2),True,fic_excel,pond,False,False,res[1],chemin_crue_10,nom_fic_str,nom_cal,nom_ecart)
            n_pond=0
            #calcul de l erreur de validation a partir des resultats du recuit
            for l in range(len(pond)):
                if(pond[l]==1):
                    n_pond=n_pond+1
                    erreur_validation=erreur_validation+res1[2][l]
            erreur_validation=erreur_validation/(n_pond)
            err_tot=float(pond_val[0])*erreur_apprentissage+float(pond_val[1])*erreur_validation
        else:
            err_tot=erreur_apprentissage

        #affichage et ecriture des resultats pour la combinaison en cours
        print "erreur val =" ,erreur_validation
        print "erreur apprentissage=",erreur_apprentissage
        print "erreur totale",err_tot
        chaine=str(" pond "+str(ponderation)+" err_app "+str(round(erreur_apprentissage,2))+" err_val "+str(round(erreur_validation,2))+" err_tot "+str(round(err_tot,2))+str(res1[2]))
        with open('trajectoire_cv.txt','a') as fic:
            fic.write(str(chaine+"\n"))
            
        #mise a jour du minimum et des parametres optimaux si valeur courante inferieure
        if(err_tot<erreur_min):
            erreur_min=err_tot
            Param_min=res[0]
            debit_min=res1[1]
            ponderation_min=ponderation
        j=j+1

    print "fin de la validation croisee"

    #Ecriture resultats globaux etexecution pour mettre a jour les .xml avec les meilleurs parametres
    resultat=crit.import_Stricklers(fic_excel)
    nom_loi=resultat[0]
    Param_init=resultat[1]
    resultat=crit.import_debit(fic_excel)
    nom_calcul=modif.lire_calcul(fic_csv_le_cal)
    nom_cl=resultat[3]
    resultat=crit.import_le_mesure(fic_excel)
    le_mes=resultat[1]
    pk=resultat[0]
    
    #changement aec les parametres optimaux
    modif.change_strickler_loi(Param_min,fichier_dfrt_cible,nom_loi)
    modif.change_debit(debit_min,fic_dclm_cible,nom_calcul,nom_cl)

    #Relance le calcul pour verifier resultat correct
    lance_otfa(sExeOtfa,fic_otfa)
    res=crit.extraction_csv_comp(pk,le_mes,fic_csv_le_cal,"le_cal_final.csv","ecart_final.csv")
    a=crit.fonc_crit_moyenne_quad(res[0],res[1],ponderation_min)
    print a[0],a[1]

    #Ecriture des parametres optimaux dans des fichiers 
    with open('resultat_stricklers_cv.csv', 'wb') as fic:
        writer = csv.writer(fic,delimiter=";")
        writer.writerow(["nv parametres","old parametres"])
        for l in range(len(Param_min)):
            writer.writerow([str(Param_min[l]),str(Param_init[l])])
            
    with open('resultat_debit_cv.csv', 'wb') as fic:
        writer = csv.writer(fic,delimiter=";")
        for l in range(len(debit_min[:,1])):
            writer.writerow(debit_min[l,:])
    chaine=str("err_min "+str(erreur_min)+" ponderation_min "+str(ponderation_min)+str(a[0]))
    print chaine
    with open('resultat_cv.txt','wb') as fic:
        fic.write(chaine)  

#Fonction pour simuler un evenement transitoire (limnigrammes pour le moment et possiblement a plusieurs endroit mais pas plusieurs evenement en calibrer plusieurs a la suite)
def test_transitoire(sExeOtfa,fic_str_orig,fic_str_copie,fic_calc_csv,nom_otfa,fic_excel):

    #copie du fichier frottement a utiliser
    if(fic_str_orig!=fic_str_copie):
        shutil.copyfile(fic_str_orig,fic_str_copie)

    #run avec fudaa 
    lance_otfa(sExeOtfa,nom_otfa)

    #extraction des resultats
    res=crit.extraction_transitoire_comp(fic_excel,fic_calc_csv)

    #Definition de l axe temporel ici horaire
    tps=numpy.array(range(len(res[0])))
    tps=numpy.hstack((tps[:,numpy.newaxis],tps[:,numpy.newaxis]))

    #graphique des resultats avec un graphique pour chaque limnigramme mesure
    if (len(res[2][1,:])>2):
        for l in range(len(res[1][1,:])):
            plt.figure()
            val=numpy.hstack((res[1][:,l],res[2][:,l]))
            plt.plot(tps,val)
            plt.xlabel("temps")
            plt.ylabel("cote")
            plt.legend(["val mesuree","val calculee"])
            plt.grid(True)
            plt.savefig(str("Limnigramme"+str(l)+"png"),format="png")
            plt.show(block=False)
    else:
        resint=numpy.array(numpy.reshape(res[2][:,0],len(res[0])))
        resint2=numpy.array(numpy.reshape(res[1],len(res[0])))
        val=numpy.hstack((resint2[:,numpy.newaxis],resint[:,numpy.newaxis]))
        plt.figure()
        plt.plot(tps,val)
        plt.xlabel("temps")
        plt.ylabel("cote")
        plt.legend(["val mesuree","val calculee"])
        plt.grid(True)
        plt.savefig("Limnigramme.png",format="png")
        plt.show(block=False)

#fonction qui initialise tous les chemins et variables globales a l aide du classeur excel
def Init_process(fic_excel):
    global sExeOtfa,fic_otfa,temps_alloue,fichier_dfrt_cible,fichier_dfrt_ori,fic_csv_le_cal,fic_dclm_cible,fic_dclm_ori,otfa_trans,otfa_trans_rapport,fic_dfrt_trans_orig,fic_dfrt_trans_cible,iftransitoire,ponderation,gamme_q,effectif,pond_val,if_cv,if_mont,chemin_crue_10,if_AS
    chemin=crit.import_chemin(fic_excel)
    sExeOtfa = chemin[0]
    fic_otfa =chemin[1]
    temps_alloue=chemin[2]
    fichier_dfrt_cible=chemin[3]
    fichier_dfrt_ori=chemin[4]
    fic_csv_le_cal=chemin[5]
    fic_dclm_cible=chemin[6]
    fic_dclm_ori=chemin[7]
    chemin_crue_10=chemin[9]
    if_AS=bool(float(chemin[10])>0)
    if_mont=bool(float(chemin[8])>0)
    chemin=crit.import_chemin_trans(fic_excel)
    iftransitoire=bool(float(chemin[0])>0)
    otfa_trans=chemin[1]
    otfa_trans_rapport=chemin[2]
    fic_dfrt_trans_orig=chemin[3]
    fic_dfrt_trans_cible=chemin[4]
    chemin=crit.import_validation_croisee(fic_excel)
    ponderation=chemin[1]
    gamme_q=chemin[2]
    effectif=chemin[3]
    pond_val=chemin[4][0:2]
    if_cv=bool(float(chemin[5][0])>0)


#definition de ce qui va etre execute en commande
def Main():
    #prend l argument place apres le py en ligne de commane (ici classeur excel)
    fic_excel=sys.argv[1]
    #Initialiser chemins et bornes
    Init_process(fic_excel)
    if(if_cv):
        print("validation_croisee")
        validation_croisee(sExeOtfa,fic_otfa,fichier_dfrt_cible,fichier_dfrt_ori,fic_dclm_ori,fic_dclm_cible,fic_csv_le_cal,temps_alloue,True,fic_excel,gamme_q,effectif,pond_val,chemin_crue_10)
    elif (if_mont):
        Montecarlo(sExeOtfa,fic_otfa,fichier_dfrt_cible,fichier_dfrt_ori,fic_dclm_ori,fic_dclm_cible,fic_csv_le_cal,temps_alloue,fic_excel,ponderation,chemin_crue_10,"LE_cal.csv","ecarts.csv")
    elif(iftransitoire):
        Simulated_Annealing_trans_rapide(sExeOtfa,otfa_trans,fic_dfrt_trans_cible,fic_dfrt_trans_orig,otfa_trans_rapport,temps_alloue,fic_excel,True,chemin_crue_10)
    elif(if_AS):
         dummy="dummy"
         analyse_sensibilite(sExeOtfa,fic_otfa,fichier_dfrt_cible,fichier_dfrt_ori,fic_dclm_ori,fic_dclm_cible,fic_csv_le_cal,temps_alloue,True,fic_excel,True,True,dummy,chemin_crue_10)
    else:                         
        dummy="dummy"
        Simulated_Annealing(sExeOtfa,fic_otfa,fichier_dfrt_cible,fichier_dfrt_ori,fic_dclm_ori,fic_dclm_cible,fic_csv_le_cal,temps_alloue,True,fic_excel,ponderation,True,True,dummy,chemin_crue_10,"resultat_stricklers.csv","LE_cal.csv","ecarts.csv")
    
    #os.system("pause")
    plt.close("all")

#fonction du main 
Main()

#bloc pour tester le script avec l interpreteur et non en ligne de commande utile pour deboguer
#resultat=crit.import_transitoire("test_classeur_LE_zone.xlsm")
#dico_section=resultat[0]
#res_ref=resultat[1]
#dico_temps=resultat[2]
#nom_cal=resultat[3]
#dico_res_ref=lbin.resultat_crit(res_ref,dico_temps,nom_cal,dico_section)
