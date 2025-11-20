from hielen3.feature import HFeature
from hielen3.contextmanager import manage_feature_context



a=["001CE01_DL","001CE02_DL","001VB01_DL","001VB02_DL","002CE01_DL","002VB01_DL","003CE01_DL","003VB01_DL"]


def creacose(lista, context, ftype):
    for n in lista:
        print (n)
        a=HFeature.create(ftype,label=n)
        manage_feature_context(a.uuid,context)
    
