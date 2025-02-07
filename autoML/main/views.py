from django.shortcuts import render
from utils import get_db_mongo
from django.contrib.auth.decorators import login_required
import pandas as pd
from pymongo import MongoClient

# Create your views here.
def home(request):
    return render(request, 'accueil.html')

@login_required
def espace_personel(request):
    username=request.user.username
    return render(request, 'espace_perso.html',{'username': username})

class Df_perso:
    def __init__(self,df):
        self.df=df.copy()
    def info_df(self):
        self.ligne = self.df.shape[0]
        self.colonne = self.df.shape[1]
        self.nb_nul = self.df.isnull().sum().to_frame().to_html()
        self.nb_colonne_double = self.df.duplicated().sum()
        return {'ligne':self.ligne,'colonne':self.colonne,
                'nb_nul':self.nb_nul,'nb_colonne_double':self.nb_colonne_double}
    def magic_clean(self):
        for col in self.df.select_dtypes(include=['object']).columns:
            self.df[col] = self.df[col].astype(str).str.replace(r'[\s\x00-\x1F\x7F-\x9F]+', '', regex=True)
            self.df[col] = pd.to_numeric(self.df[col], errors='ignore')
            self.df[col] = self.df[col].astype(str).str.replace(',', '.', regex=False)
            try :
                converted = pd.to_numeric(self.df[col], errors='raise')
                if converted.notna().all():
                    try:
                        self.df[col]=self.df[col].astype(int)
                    except:
                        self.df[col]=self.df[col].astype(float)
            except :
                test1=self.df[col].apply(lambda x: isinstance(x, dict)).all()
                test2=self.df[col].apply(lambda x: isinstance(x, list)).all()
                if test1==True or test2==True:
                    pass
                else:
                    self.df[col]=self.df[col].astype(str)
        return self.df
    def type_column(self):
        df_cleaned=self.magic_clean()
        self.categorical_column=df_cleaned.select_dtypes(include=["category",'object']).columns.tolist()
        self.numerical_column=df_cleaned.select_dtypes(include=['number']).columns.tolist()
        return self.categorical_column, self.numerical_column
    def colonne_type(self):
        return {
            col: type(self.df[col].dropna().iloc[0]).__name__ if not self.df[col].dropna().empty else 'NoneType'
            for col in self.df.columns
        }
    def afficher_df(self):
        self.columns=self.df.columns   
        self.dico_type=self.colonne_type()
        self.rows = self.df.reset_index().to_dict(orient='records')
        return self.columns,self.dico_type,self.rows

class Bdd_user:
    def __init__(self,db_name_m,host_m,port_m,username_m,password_m):
        self.db_name_m=db_name_m
        self.host_m=host_m
        self.port_m=port_m
        self.username_m=username_m
        self.password_m=password_m
    def get_db_mongo(self):
        self.client = MongoClient(host=self.host_m,
                            port=int(self.port_m),
                            username=self.username_m,
                            password=self.password_m
                            )
        self.db_mongo = self.client[self.db_name_m]
        return self.db_mongo, self.client

    