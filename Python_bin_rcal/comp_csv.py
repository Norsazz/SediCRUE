#*-*- coding:Latin-1-*
import os
import string
import csv
import subprocess
from numpy  import *
import xlrd
import datetime

#Fonction pour extraire les valeurs de la cote des lignes d'eau
# simulees et mesurees

# Arguments - chemin fichier des cotes mesurees rempli manuellement
#- chemin fichier cotes simulees avec rapport otfa comforme avce cotes mesurees 

# Attention le critère pour extraire sont les P du fichier des cotes mesurees
def import_le_mesure(fic_excel):
    pk=list()
    book=xlrd.open_workbook(fic_excel)
    sh = book.sheet_by_name("LE_mesuree")
    nrows=sh.nrows
    ncols=sh.ncols
    nb_ligne_eau=ncols-1
    LE_mes=zeros((nrows-1,nb_ligne_eau))
    for rx in range(1,nrows):
        cells=sh.row_slice(rowx=rx)
        j=0
        for cell in cells:
            if(j==0):
                pk.append(str(cell.value))
            else:
                if(cell.value==""):
                    LE_mes[rx-1,j-1]=-1
                else:
                    LE_mes[rx-1,j-1]=cell.value 
            j=j+1
    return pk,LE_mes


def import_debit(fic_excel):
    cl=list()
    book=xlrd.open_workbook(fic_excel)
    sh = book.sheet_by_name("Debit")
    nrows=sh.nrows
    ncols=sh.ncols
    nb_ligne_eau=(ncols-1)/2
    Debit=zeros((nrows-1,nb_ligne_eau))
    ampli=zeros((nrows-1,nb_ligne_eau))
    for rx in range(1,nrows):
        cells=sh.row_slice(rowx=rx)
        j=0
        for cell in cells:
            if(j==0):
                cl.append(str(cell.value))
            else:
                if(j>nb_ligne_eau):
                    ampli[rx-1,j-nb_ligne_eau-1]=cell.value 
                else:
                    Debit[rx-1,j-1]=cell.value 
            j=j+1
    Debit_maxi=Debit+Debit*ampli
    Debit_mini=Debit-Debit*ampli
    return Debit,Debit_mini,Debit_maxi,cl

def import_Stricklers(fic_excel):
    loi=list()
    Str_ini=list()
    Str_min=list()
    Str_max=list()
    book=xlrd.open_workbook(fic_excel)
    sh = book.sheet_by_name("Stricklers")
    nrows=sh.nrows
    ncols=sh.ncols
    for rx in range(1,nrows):
        cells=sh.row_slice(rowx=rx)
        j=0
        for cell in cells:
            if(j==0):
                loi.append(str(cell.value))
            elif(j==1):
                Str_ini.append(float(cell.value))
            elif(j==2):
                Str_min.append(float(cell.value))
            else:
                Str_max.append(float(cell.value))  
            j=j+1
    return loi,Str_ini,Str_min,Str_max

def import_chemin(fic_excel):
    book=xlrd.open_workbook(fic_excel)
    sh = book.sheet_by_name("Chemins")
    nrows=sh.nrows
    ncols=sh.ncols
    liste_chemin=list()
    for rx in range(nrows):
        cells=sh.row_slice(rowx=rx)
        j=0
        for cell in cells:
            if(j>0 and cell.value!=""):
                liste_chemin.append(str(cell.value))
            j=j+1
    return liste_chemin

def import_chemin_trans(fic_excel):
    book=xlrd.open_workbook(fic_excel)
    sh = book.sheet_by_name("Chemin_transitoire")
    nrows=sh.nrows
    ncols=sh.ncols
    liste_chemin=list()
    for rx in range(nrows):
        cells=sh.row_slice(rowx=rx)
        j=0
        for cell in cells:
            if(j>0 and cell.value!=""):
                liste_chemin.append(str(cell.value))
            j=j+1
    return liste_chemin

def import_transitoire(fic_excel):
    book=xlrd.open_workbook(fic_excel)
    sh = book.sheet_by_name("Transitoire")
    nrows=sh.nrows
    ncols=sh.ncols
    nom_cal=list()
    nombre_section=list()
    dico_section=dict()
    res_ref=dict()
    dico_temps=dict()
    i=0
    for rx in range(nrows):
        cells=sh.row_slice(rowx=rx)
        if(i==0):
            j=0
            for cell in cells:
                if(j>0 and cell.value!=""):
                    nom_cal.append(str(cell.value))
                j=j+1
        elif(i==1):
            j=0
            for cell in cells:
                if(j>0):
                    nombre_section.append(int(cell.value))
        elif(i>1):
            j=0
            bool_test=False
            for cell in cells:
                if(j==0):
                    nom_ref=str(cell.value)
                elif(j==1 and str(cell.value)=="temps"):
                    bool_test=True
                    dico_temps[nom_ref]=list()
                    dico_section[nom_ref]=list()
                    res_ref[nom_ref]=dict()
                elif (j==1 and cell.value!=""):
                    dico_temps[nom_ref].append(int(cell.value))
                elif(j>1 and bool_test==True and cell.value!=""):
                    dico_section[nom_ref].append(str(cell.value))
                    res_ref[nom_ref][cell.value]=list()
                elif(cell.value!=""):
                    res_ref[nom_ref][dico_section[nom_ref][j-2]].append(float(cell.value))
                j=j+1
        i=i+1
    return dico_section,res_ref,dico_temps,nom_cal

def import_validation_croisee(fic_excel):
    book=xlrd.open_workbook(fic_excel)
    sh = book.sheet_by_name("Validation_croisee")
    nrows=sh.nrows
    ncols=sh.ncols
    liste_chemin=list()
    for rx in range(nrows):
        cells=sh.row_slice(rowx=rx)
        j=0
        liste_cellule=list()
        for cell in cells:
            if(j>0 and cell.value!=""):
                liste_cellule.append(str(cell.value))
            j=j+1
        liste_chemin.append(liste_cellule)
    return liste_chemin
    
    
def extraction_transitoire(fic1,fic2):
    liste_temps=list()
    liste_valeurs=list()
    #lecture fichier temps valeur transitoire
    fic_mes=open(fic1,"rb")
    cr=csv.reader(fic_mes,delimiter=";")
    i=0
    j=0
    for row in cr:
        if (j>0 ):
            liste_temps.append(row[0])
            liste_valeurs.append(float(row[1]))
        j=j+1

    fic_mes.close()
    #lecture fichier exporte par fudaa
    fic_cal=open(fic2,"rb")
    cr2 = csv.reader(fic_cal,delimiter=";")
    i=0
    j=0
    LE_cal=zeros(len(liste_temps))
    for row2 in cr2:
        if(j>4):
            if (i<len(liste_temps)):
                if(row2[1].find(liste_temps[i])>-1):
                    LE_cal[i]=float(row2[2])
                    i=i+1
                    j=j+1
                else:
                    j=j+1
        else:
            j=j+1

    fic_cal.close()
    a=array(liste_valeurs)
    LE_cal=array(LE_cal)
    c1 = csv.writer(open("res_cal_trans.csv", "wb"),delimiter=";")
    for j in range(len(liste_temps)):
        l=list()
        l.append(liste_temps[j])
        l.append(str(LE_cal[j]))
        c1.writerow(l)
        
    c = csv.writer(open("ecarts_transitoire.csv", "wb"),delimiter=";")
    for j in range(len(liste_temps)):
        l=list()
        l.append(str((LE_cal[j]-a[j])*100.0))
        c.writerow(l)
    return a, LE_cal


def crit_transitoire_comp(fic_excel,fic2):
    liste_temps=list()
    #lecture fichier temps valeur transitoire
    book=xlrd.open_workbook(fic_excel)
    sh = book.sheet_by_name("Limnigramme")
    nrows=sh.nrows
    ncols=sh.ncols
    liste_valeurs=zeros((nrows-1,ncols-1))
    for rx in range(1,nrows):
        cells=sh.row_slice(rowx=rx)
        j=0
        for cell in cells:
            if j==0 :    
                liste_temps.append(date_conv(cell.value))
            else:
                liste_valeurs[rx-1,j-1]=float(cell.value)
            j=j+1
            
    #lecture fichier exporte par fudaa
    fic_cal=open(fic2,"rb")
    cr2 = csv.reader(fic_cal,delimiter=";")
    i=0
    j=0
    len_temps=0
    liste_temps2=list()
    for row2 in cr2:
        if(j>4):
            len_temps=len_temps+1
        j=j+1
        
    j=0
    fic_cal.close()
    fic_cal=open(fic2,"rb")
    cr2 = csv.reader(fic_cal,delimiter=";")
    LE_cal=zeros((len_temps,ncols))
    print size(LE_cal,0)
    print size(LE_cal,1)
    for row2 in cr2: 
        if(j>4):
            liste_temps2.append(date_conv(row2[1]))
            for l in range(ncols-1):
                LE_cal[i,l]=float(row2[l+2])
            i=i+1
            j=j+1
        else:
            j=j+1

    fic_cal.close()
    a=array(liste_valeurs)
    LE_cal=array(LE_cal)
    c1 = csv.writer(open("res_cal_trans.csv", "wb"),delimiter=";")
    for j in range(len(liste_temps2)):
        liste=list()
        liste.append(liste_temps2[j])
        for l in range(ncols-1):
            liste.append(str(LE_cal[j,l]))
        c1.writerow(liste)
    
    return liste_temps,liste_temps2,LE_cal,liste_valeurs

def crit_trans_cal(liste_temps,Liste_valeurs,liste_temps2,LE_cal):
    lmax1=list()
    lmax2=list()
    vol1=list()
    vol2=list()
    tps_max1=list()
    tps_max2=list()
    for i in range(len(LE_cal[1,])-1):
        lmax1.append(max(LE_cal[:,i]))
        indice_max1=list()
        volume=0
        for j in range(len(liste_temps2)):
            if(lmax1[i]==LE_cal[j,i]):
                indice_max1.append(liste_temps2[j])
            if(j>0):
                volume=volume+(LE_cal[j,i]+LE_cal[j-1,i])/2.0*(liste_temps2[j]-liste_temps2[j-1])
        vol1.append(volume)
        tps_max1.append(max(indice_max1))               
                       
    for i in range(len(Liste_valeurs[1,])):
        lmax2.append(max(Liste_valeurs[:,i]))
        indice_max2=list()
        volume=0
        for j in range(len(liste_temps)):
            if(lmax2[i]==Liste_valeurs[j,i]):
                indice_max2.append(liste_temps[j])
                print lmax2,indice_max2
            if(j>0):
                volume=volume+(Liste_valeurs[j,i]+Liste_valeurs[j-1,i])/2.0*(liste_temps[j]-liste_temps[j-1])
        vol2.append(volume)
        
        tps_max2.append(max(indice_max2))
    dmax=list()
    dvol=list()
    dtps_max=list()
    dmaxm=0.0
    dvolm=0.0
    dtps_maxm=0.0
    for i in range(len(lmax1)):
        dmax.append(abs(lmax1[i]-lmax2[i])/lmax2[i])
        dmaxm=dmaxm+dmax[i]/len(lmax1)
        dvol.append(abs(vol1[i]-vol2[i])/vol2[i])
        dvolm=dvolm+dvol[i]/len(lmax1)
        dtps_max.append(abs(float(tps_max2[i]-tps_max1[i]))/tps_max2[i])
        dtps_maxm=dtps_maxm+dtps_max[i]/len(lmax1)
    return dmax,dvol,dtps_max,dmaxm,dvolm,dtps_maxm 
        
    

def extraction_transitoire_comp(fic_excel,fic2):
    liste_temps=list()
    #lecture fichier temps valeur transitoire
    book=xlrd.open_workbook(fic_excel)
    sh = book.sheet_by_name("Limnigramme")
    nrows=sh.nrows
    ncols=sh.ncols
    liste_valeurs=zeros((nrows-1,ncols-1))
    for rx in range(1,nrows):
        cells=sh.row_slice(rowx=rx)
        j=0
        for cell in cells:
            if(j==0):
                #date_val=xlrd.xldate_as_tuple(cell.value,book.datemode)
                #liste_temps.append(str(datetime.time(*date_val[3:])))
                liste_temps.append(date_conv(cell.value))
            else:
                liste_valeurs[rx-1,j-1]=float(cell.value)
            j=j+1
    #lecture fichier exporte par fudaa
    fic_cal=open(fic2,"rb")
    cr2 = csv.reader(fic_cal,delimiter=";")
    i=0
    j=0
    LE_cal=zeros((len(liste_temps),ncols))
    for row2 in cr2:
        if(j>4):
            if (i<len(liste_temps)):
                if(date_conv(row2[1])==liste_temps[i]):
                    for l in range(ncols-1):
                        LE_cal[i,l]=float(row2[l+2])
                    i=i+1
                j=j+1
        else:
            j=j+1

    fic_cal.close()
    a=array(liste_valeurs)
    LE_cal=array(LE_cal)
    c1 = csv.writer(open("res_cal_trans.csv", "wb"),delimiter=";")
    for j in range(len(liste_temps)):
        liste=list()
        liste.append(liste_temps[j])
        for l in range(ncols-1):
            liste.append(str(LE_cal[j,l]))
        c1.writerow(liste)
        
    c = csv.writer(open("ecarts_transitoire.csv", "wb"),delimiter=";")
    for j in range(len(liste_temps)):
        liste=list()
        for l in range(ncols-1):
            liste.append(str((LE_cal[j,l]-a[j,l])*100.0))
        c.writerow(liste)
    return liste_temps,a, LE_cal
    
def extraction_csv_comp(pk,le_mes,fic2,nom_cal,nom_ecart):
    dico_dist=dict()
    nb_ligne_eau=len(le_mes[1,:])
    #Remplir le tableau des cotes simulees pour comparer avec mesures
    fic_cal=open(fic2,"rb")
    cr2 = csv.reader(fic_cal,delimiter=";")
    i=0
    j=0
    LE_cal=zeros((len(pk),nb_ligne_eau))
    distance=zeros(len(pk))
    liste_nom_modele=list()
    pk2=list(pk)
    for row2 in cr2:
        if(j>4):
            if (i<len(pk)):
                if(True in [row2[0].find(pk2[l])>-1 for l in range(len(pk2))]):
                    test=[row2[0].find(pk2[l])>-1 for l in range(len(pk2))]
                    ind=test.index(True)
                    liste_nom_modele.append(pk2[ind])
                    pk2[ind]="section_passee"
                    if float(row2[1])>100.0:
                        distance[i]=float(row2[1])*1.0/1000.0
                        dico_dist[pk[ind]]=float(row2[1])*1.0/1000.0
                    else:
                        distance[i]=float(row2[1])
                        dico_dist[pk[ind]]=float(row2[1])
                    for k in range(nb_ligne_eau):
                            LE_cal[ind,k]=float(row2[k+2])
                    i=i+1
                if(True in [row2[0].find(pk2[l])>-1 for l in range(len(pk2))]):
                    test=[row2[0].find(pk2[l])>-1 for l in range(len(pk2))]
                    ind=test.index(True)
                    liste_nom_modele.append(pk2[ind])
                    pk2[ind]="section_passee"
                    if float(row2[1])>100.0:
                        distance[i]=float(row2[1])*1.0/1000.0
                        dico_dist[pk[ind]]=float(row2[1])*1.0/1000.0
                    else:
                        distance[i]=float(row2[1])
                        dico_dist[pk[ind]]=float(row2[1])
                    for k in range(nb_ligne_eau):
                            LE_cal[ind,k]=float(row2[k+2])
                    i=i+1
                
                else:
                    j=j+1
        else:
            j=j+1

    fic_cal.close()
    if_mesure=le_mes>0
    le_mes=le_mes*if_mesure
    c1 = csv.writer(open(nom_cal, "wb"),delimiter=";")
    for j in range(len(pk)):
        l=list()
        distance[j]=dico_dist[pk[j]]
        #l.append(liste_nom_modele[j])
        l.append(pk[j])
        for k in range(nb_ligne_eau):
                l.append(str(LE_cal[j,k]))
        c1.writerow(l)
    LE_cal_vrai=LE_cal
    LE_cal=LE_cal*if_mesure
    c = csv.writer(open(nom_ecart, "wb"),delimiter=";")
    for j in range(len(pk)):
        l=list()
        for k in range(nb_ligne_eau):
            if (if_mesure[j,k]):
                l.append(str((LE_cal[j,k]-le_mes[j,k])*100.0))
            else:
                l.append("x")
        c.writerow(l)
    return le_mes, LE_cal,LE_cal_vrai,distance,dico_dist


def fonc_critere_trans(dico_ref,dico_cal,nom_cal,dico_section):
    resu=dict()
    res_calcul=list()
    for sec in nom_cal:
        resu[sec]=dict()
        for test in dico_section[sec]:
            resu[sec][test]=list()
            for i in range(len(dico_ref[sec][test])):
                resu[sec][test].append(abs(float(dico_ref[sec][test][i])-float(dico_cal[sec][test][i]))/float(dico_ref[sec][test][i]))
    dmax=list()
    dvol=list()
    dtps=list()
    dm_max=0
    dm_vol=0
    dm_tps=0
    effectif=0
    for sec in nom_cal:
        dm=list()
        dv=list()
        dt=list()
        for test in dico_section[sec]:
            effectif=effectif+1
            a=resu[sec][test]
            dm_max=dm_max+a[0]
            dm_vol=dm_vol+a[1]
            dm_tps=dm_tps+a[2]
            dm.append(a[0])
            dv.append(a[1])
            dt.append(a[2])
        dmax.append(dm)
        dvol.append(dv)
        dtps.append(dt)
        dm_max=dm_max/effectif
        dm_vol=dm_vol/effectif
        dm_tps=dm_tps/effectif
        
    return resu,dmax,dvol,dtps,dm_max,dm_vol,dm_tps
    
    
#fonction pour convertir jj:hh:mm:ss en secondes
def date_conv(date):
    temp=date.split(":")
    res=0
    jour=24*3600
    temps=[jour,3600,60,1]
    for i in range(4):
        res=res+temps[i]*int(temp[i])
    return res
# Fonction critere possibles pour comparer les lignes eau

#fonction donnant les moyennes des valeurs absolues pour chaque ligne d eau et le max de la liste
def fonc_crit_moyenne_abs(tableau_1,tableau_2,ponderation):
    bool_true=tableau_1>0
    a=array(ponderation)
    a=a.astype("float")
    effectif=a.sum()
    val_abs=abs(tableau_1-tableau_2)
    n_row,n_column=tableau_1.shape
    n_row=int(n_row)
    n_column=int(n_column)
    val_moy=0
    liste_moy=zeros(n_column)
    for l in range(n_column):
        liste_moy[l]=round(100*val_abs[:,l].sum()/float(bool_true[:,l].sum()),3)
        val_moy=val_moy+float(ponderation[l])*(val_abs[:,l].sum()/float(bool_true[:,l].sum()))/effectif
    val_moy=val_moy*100
    return liste_moy,val_moy

def fonc_crit_ecart_ref_cal(tableau_1,tableau_2,ponderation):
    bool_true=tableau_1>0
    a=array(ponderation)
    a=a.astype("float")
    effectif=a.sum()
    val_abs=tableau_2
    n_row,n_column=tableau_1.shape
    n_row=int(n_row)
    n_column=int(n_column)
    val_moy=0
    liste_moy=zeros(n_column)
    for l in range(n_column):
        nb=array(val_abs[:,l]>0).sum()
        liste_moy[l]= round(val_abs[:,l].sum()/nb,3)
        val_moy=val_moy+float(ponderation[l])*(100*val_abs[:,l].sum()/(nb))
    val_moy=val_moy
    return liste_moy,val_moy

#fonction donnant l ecart absolu max pour chaque ligne d eau et le max de la liste
def fonc_crit_moyenne_max(tableau_1,tableau_2,ponderation):
    bool_true=tableau_1>0
    a=array(ponderation)
    a=a.astype("float")
    effectif=a.sum()
    val_abs=abs(tableau_1-tableau_2)
    n_row,n_column=tableau_1.shape
    n_row=int(n_row)
    n_column=int(n_column)
    val_moy=0
    liste_moy=zeros(n_column)
    for l in range(n_column):
        liste_moy[l]=round(100*max(val_abs[:,l],3))
        val_moy=val_moy+float(ponderation[l])*max(val_abs[:,l])/effectif
    val_moy=val_moy*100
    return liste_moy,val_moy

#fonction donnant les moyennes des ecarts quadratiques pour chaque ligne d eau et le max de la liste
def fonc_crit_moyenne_quad(tableau_1,tableau_2,ponderation):
    bool_true=tableau_1>0
    a=array(ponderation)
    a=a.astype("float")
    effectif=a.sum()
    val_abs=abs(tableau_1-tableau_2)*abs(tableau_1-tableau_2)
    n_row,n_column=tableau_1.shape
    n_row=int(n_row)
    n_column=int(n_column)
    val_moy=0
    liste_moy=zeros(n_column)
    for l in range(n_column):
        liste_moy[l]=round(100*sqrt(val_abs[:,l].sum()/float(bool_true[:,l].sum())),3)
        val_moy=val_moy+float(ponderation[l])*sqrt((val_abs[:,l].sum()/float(bool_true[:,l].sum())))/effectif
    val_moy=val_moy*100
    return liste_moy,val_moy

#fonction donnant la valeur du quantile a ...%  pour chaque ligne d eau et le max de la liste
def fonc_crit_moyenne_quantile(tableau_1,tableau_2,quantile,ponderation):
    bool_true=tableau_1>0
    a=array(ponderation)
    a=a.astype("float")
    effectif=a.sum()
    val_abs=abs(tableau_1-tableau_2)
    n_row,n_column=tableau_1.shape
    n_row=int(n_row)
    n_column=int(n_column)
    val_moy=0
    liste_moy=zeros(n_column)
    for l in range(n_column):
        tri=sort(val_abs[:,l])
        nb_mes=n_row-bool_true[:,l].sum()+int(quantile*bool_true[:,l].sum())
        liste_moy[l]=round(100*tri[nb_mes],3)
        val_moy=val_moy+float(ponderation[l])*tri[nb_mes]/effectif
    val_moy=val_moy*100/n_column
    return liste_moy,val_moy
#test extraction 
#res=extraction_csv("LE_comp.csv","resst1.csv")
#res=crit_transitoire_comp("test_classeur_LE_zone.xlsm","res_trans.csv")
#liste_temps,liste_temps2,LE_cal,Liste_valeurs
#a=crit_trans_cal(res[0],res[3],res[1],res[2])
#a=fonc_crit_moyenne_abs(res[0],res[1])
#a=fonc_crit_moyenne_quad(res[0],res[1])
#a=fonc_crit_moyenne_max(res[0],res[1])
#a=fonc_crit_moyenne_quantile(res[0],res[1],0.68)
#res=import_validation_croisee("test_classeur.xlsx")
#res=import_transitoire("test_classeur_LE_zone.xlsm")
