import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

np.random.seed(10)
df = pd.DataFrame({'a': np.random.normal(100, 20, 200),
                   'b': np.random.normal(100, 20, 200),
                   'c': np.random.normal(100, 20, 200)})

df2 = pd.DataFrame({'a': [1, 2, 2, 3, 4, 4, 4, 4, 4, 5, 5,0,0]}
)

def col_type(df):
    response= df.dtypes
    return dict(response)

def boxplot(df_num):
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.boxplot(df_num.values, tick_labels=df_num.columns,vert=True)
    ax.set_xlabel("Valeurs")
    ax.set_ylabel("Colonnes")
    plt.grid()
    return fig

def histplot(df):
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.hist(df.values, bins=5)
    ax.set_xlabel("Valeurs")
    ax.set_ylabel("Colonnes")
    plt.grid()
    return fig

def scatterplot(colonne_x,colonne_y,df):
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(x=df[colonne_x], y=df[colonne_y], alpha=1, edgecolors='w',c='red')
    ax.set_xlabel(colonne_x)
    ax.set_ylabel(colonne_y)
    ax.set_title(f"Scatterplot de {colonne_x} vs {colonne_y}")
    plt.grid()
    return fig

def matrix_corr(df):
    fig=plt.figure(figsize=(16, 6))
    heatmap = sns.heatmap(df.corr(), vmin=-1, vmax=1, annot=True, cmap='BrBG')
    heatmap.set_title('Correlation Heatmap', fontdict={'fontsize':18}, pad=12)
    return fig

fig=matrix_corr(df)
plt.show()