
from celery import shared_task
import time
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
import warnings

@shared_task(bind=True)
def train_model_task(self, X_train, y_train, model_name="random_forest", params=None, use_grid_search=False, search_models=False, scoring="accuracy", cv=5):
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
    warnings.filterwarnings("ignore")

    if search_models:
        for i, (model_key, model) in enumerate(models.items()):
            try:
                self.update_state(state="PROGRESS", meta={"current_step": i+1, "total_steps": len(models), "model": model_key})
                grid_search = GridSearchCV(model, param_grid[model_key], cv=cv, scoring=scoring)
                grid_search.fit(X_train, y_train)

                if grid_search.best_score_ > best_score:
                    best_score = grid_search.best_score_
                    best_model = grid_search.best_estimator_
                    best_params = grid_search.best_params_

            except Exception as e:
                return {"status": "FAILED", "error": str(e)}

        return {"status": "COMPLETED", "best_model": str(best_model), "best_params": best_params}

    else:
        model = models.get(model_name)
        if model is None:
            return {"status": "FAILED", "error": f"Modèle '{model_name}' non reconnu."}

        try:
            if use_grid_search:
                self.update_state(state="PROGRESS", meta={"message": f"Recherche des meilleurs paramètres pour {model_name}..."})
                grid_search = GridSearchCV(model, param_grid[model_name], cv=cv, scoring=scoring)
                grid_search.fit(X_train, y_train)
                return {"status": "COMPLETED", "best_model": str(grid_search.best_estimator_), "best_params": grid_search.best_params_}

            elif params:
                model.set_params(**params)

            model.fit(X_train, y_train)
            return {"status": "COMPLETED", "best_model": str(model), "params": params}

        except Exception as e:
            return {"status": "FAILED", "error": str(e)}