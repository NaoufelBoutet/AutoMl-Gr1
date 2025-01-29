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


def train_model(X_train, y_train, model_name="random_forest", params=None, use_grid_search=False, search_models=False, scoring="accuracy", cv=5):
    models = {
        "random_forest": RandomForestClassifier(),
        "svm": SVC(),
        "logistic_regression": LogisticRegression()
    }
    param_grid = {
        "random_forest": {"n_estimators": [10, 50, 100], "max_depth": [None, 10, 20]},
        "svm": {"C": [0.1, 1, 10], "kernel": ["linear", "rbf"]},
        "logistic_regression": {"C": [0.1, 1, 10], "solver": ["liblinear"]}
    }
    best_model = None
    best_score = float('-inf')
    best_params = None
    models_tested = 0  # Compteur des modèles testés avec succès
    message={}
    warnings.filterwarnings("ignore")
    if search_models:
            for model_key, model in models.items():
                try:
                    print(f"🔍 Optimisation du modèle: {model_key} avec scoring={scoring} et cv={cv}")
                    grid_search = GridSearchCV(model, param_grid[model_key], cv=cv, scoring=scoring)
                    grid_search.fit(X_train, y_train)

                    models_tested += 1  # Incrémenter si le modèle a fonctionné

                    if grid_search.bestscore > best_score:
                        best_score = grid_search.bestscore
                        best_model = grid_search.bestestimator
                        best_params = grid_search.bestparams

                except Exception as e:
                    print(f"⚠️ Erreur avec le modèle {model_key}: {e}")

            if best_model is None:
                return None,None,"❌ Aucun modèle n'a réussi à s'entraîner."
            else:
                print(f"✅ Meilleur modèle trouvé: {best_model} avec score={best_score}")

            return best_model, best_params

    else:
        model = models.get(model_name)

        if model is None:
            print(f"❌ Modèle '{model_name}' non reconnu. Choisissez parmi {list(models.keys())}.")
            return None, None

        try:
            if use_grid_search:
                print(f"🔍 Recherche des meilleurs paramètres pour {model_name}...")
                grid_search = GridSearchCV(model, param_grid[model_name], cv=cv, scoring=scoring)
                grid_search.fit(X_train, y_train)
                return grid_search.bestestimator, grid_search.bestparams

            elif params:
                model.set_params(**params)

            print(f"🚀 Entraînement du modèle {model_name}...")
            model.fit(X_train, y_train)
            return model, params

        except Exception as e:
            print(f"⚠️ Erreur avec {model_name}: {e}")

        return None, None