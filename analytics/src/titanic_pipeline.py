"""Reproducible Titanic EDA and modeling pipeline for the Zepto capstone."""
from pathlib import Path
import json

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score, mean_absolute_error,
                             mean_squared_error, precision_score, r2_score, recall_score, roc_auc_score, roc_curve)
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier, plot_tree
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
ARTIFACTS.mkdir(exist_ok=True)
RANDOM_STATE = 42


def load_once():
    """Load from Seaborn once, then save the required offline fallback immediately."""
    csv_path = ROOT / "titanic.csv"
    try:
        frame = sns.load_dataset("titanic")
    except Exception:
        if not csv_path.exists():
            raise RuntimeError("Seaborn could not download titanic and no titanic.csv fallback exists")
        frame = pd.read_csv(csv_path)
    frame.to_csv(csv_path, index=False)
    return frame


def profile(frame):
    missing = (frame.isna().mean() * 100).loc[lambda series: series > 0].round(2).to_dict()
    print(frame.info())
    print(frame.describe(include="all"))
    print("shape:", frame.shape)
    print("missing_percentages:", missing)
    return missing


def clean(frame, missing):
    cleaned = frame.copy()
    # Under 5%: drop affected rows. Between 5% and 30%: impute. Above 30%: drop unreliable column.
    high_missing = [column for column, percentage in missing.items() if percentage > 30]
    cleaned = cleaned.drop(columns=["deck"] if "deck" in high_missing else [])
    for column, percentage in missing.items():
        if column not in cleaned:
            continue
        if percentage < 5:
            cleaned = cleaned.dropna(subset=[column])
        elif percentage <= 30:
            if pd.api.types.is_numeric_dtype(cleaned[column]):
                cleaned[column] = cleaned[column].fillna(cleaned[column].median())
            else:
                cleaned[column] = cleaned[column].fillna(cleaned[column].mode().iloc[0])
    return cleaned.reset_index(drop=True)


def iqr_outliers(series):
    q1, q3 = series.quantile([0.25, 0.75])
    iqr = q3 - q1
    return int(((series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)).sum())


def run_eda(frame):
    outputs = {"age_outliers": iqr_outliers(frame["age"]), "fare_outliers": iqr_outliers(frame["fare"])}
    outputs["fare_mean"] = float(frame["fare"].mean())
    outputs["fare_median"] = float(frame["fare"].median())
    outputs["fare_mode"] = float(frame["fare"].mode().iloc[0])
    outputs["survival_by_sex"] = frame.groupby("sex")["survived"].mean().round(4).to_dict()
    outputs["survival_by_pclass"] = frame.groupby("pclass")["survived"].mean().round(4).to_dict()
    outputs["survival_by_sex_pclass"] = {f"{sex}, class {pclass}": float(rate) for (sex, pclass), rate in frame.groupby(["sex", "pclass"])["survived"].mean().round(4).items()}
    correlation_columns = ["survived", "pclass", "age", "sibsp", "parch", "fare"]
    correlation = frame[correlation_columns].corr()
    pairs = []
    for index, first in enumerate(correlation_columns):
        for second in correlation_columns[index + 1:]:
            pairs.append((abs(correlation.loc[first, second]), first, second, correlation.loc[first, second]))
    outputs["strongest_correlations"] = [list(pair) for pair in sorted(pairs, reverse=True)[:2]]

    for column in ("age", "fare"):
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        sns.histplot(frame[column], kde=True, ax=axes[0])
        axes[1].boxplot(frame[column].dropna(), orientation="horizontal")
        fig.tight_layout()
        fig.savefig(ARTIFACTS / f"{column}_distribution.png")
        plt.close(fig)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    sns.barplot(data=frame, x="sex", y="survived", ax=axes[0])
    sns.barplot(data=frame, x="pclass", y="survived", ax=axes[1])
    sns.barplot(data=frame, x="pclass", y="survived", hue="sex", ax=axes[2])
    fig.tight_layout(); fig.savefig(ARTIFACTS / "survival_breakdowns.png"); plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 5)); sns.heatmap(correlation, annot=True, cmap="coolwarm", ax=ax); fig.tight_layout(); fig.savefig(ARTIFACTS / "correlation_heatmap.png"); plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].boxplot(
        [frame.loc[frame["survived"] == outcome, "fare"] for outcome in (0, 1)],
        tick_labels=["not survived", "survived"],
    )
    axes[0].set(xlabel="Survived", ylabel="Fare")
    sns.scatterplot(data=frame, x="age", y="fare", hue="survived", ax=axes[1])
    fig.tight_layout(); fig.savefig(ARTIFACTS / "multivariate_story.png"); plt.close(fig)

    standardized = frame[["age", "fare"]].copy()
    standardized[["age", "fare"]] = StandardScaler().fit_transform(standardized)
    outputs["standardized_means"] = standardized.mean().round(6).to_dict()
    outputs["standardized_stds"] = standardized.std(ddof=0).round(6).to_dict()
    return outputs


def classifier_preprocessor():
    numeric = ["age", "fare", "pclass", "sibsp", "parch"]
    categorical = ["sex", "embarked"]
    return ColumnTransformer([
        ("numeric", Pipeline([("imputer", __import__("sklearn").impute.SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric),
        ("categorical", Pipeline([("imputer", __import__("sklearn").impute.SimpleImputer(strategy="most_frequent")), ("encoder", OneHotEncoder(handle_unknown="ignore"))]), categorical),
    ])


def evaluate_classifiers(frame):
    features = ["age", "fare", "pclass", "sibsp", "parch", "sex", "embarked"]
    X_train, X_test, y_train, y_test = train_test_split(frame[features], frame["survived"], test_size=0.2, stratify=frame["survived"], random_state=RANDOM_STATE)
    estimators = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        "Decision Tree": DecisionTreeClassifier(max_depth=5, random_state=RANDOM_STATE),
        "Random Forest": RandomForestClassifier(n_estimators=150, random_state=RANDOM_STATE),
    }
    rows, fitted = [], {}
    fig, ax = plt.subplots(figsize=(8, 6))
    for name, estimator in estimators.items():
        pipeline = Pipeline([("preprocessor", classifier_preprocessor()), ("model", estimator)])
        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)
        probabilities = pipeline.predict_proba(X_test)[:, 1]
        rows.append({"model": name, "accuracy": accuracy_score(y_test, predictions), "precision": precision_score(y_test, predictions), "recall": recall_score(y_test, predictions), "f1": f1_score(y_test, predictions), "auc": roc_auc_score(y_test, probabilities)})
        fitted[name] = pipeline
        fpr, tpr, _ = roc_curve(y_test, probabilities); ax.plot(fpr, tpr, label=f"{name} AUC={rows[-1]['auc']:.3f}")
        fig_cm, cm_ax = plt.subplots(); sns.heatmap(confusion_matrix(y_test, predictions), annot=True, fmt="d", cmap="Blues", ax=cm_ax); cm_ax.set_title(name); fig_cm.savefig(ARTIFACTS / f"confusion_{name.lower().replace(' ', '_')}.png"); plt.close(fig_cm)
    ax.plot([0, 1], [0, 1], "k--"); ax.legend(); fig.tight_layout(); fig.savefig(ARTIFACTS / "roc_curves.png"); plt.close(fig)
    metrics = pd.DataFrame(rows).set_index("model")
    metrics.to_csv(ARTIFACTS / "classifier_metrics.csv")
    tree = fitted["Decision Tree"]
    fig, ax = plt.subplots(figsize=(18, 10)); plot_tree(tree.named_steps["model"], feature_names=tree.named_steps["preprocessor"].get_feature_names_out(), class_names=["not survived", "survived"], filled=True, ax=ax); fig.savefig(ARTIFACTS / "decision_tree.png"); plt.close(fig)
    return X_train, X_test, y_train, y_test, metrics, fitted


def imbalance_comparison(X_train, X_test, y_train, y_test):
    variants = {
        "baseline": RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE),
        "class_weight_balanced": RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=RANDOM_STATE),
    }
    rows = []
    for name, model in variants.items():
        pipeline = Pipeline([("preprocessor", classifier_preprocessor()), ("model", model)])
        pipeline.fit(X_train, y_train); prediction = pipeline.predict(X_test)
        rows.append({"strategy": name, "precision": precision_score(y_test, prediction), "recall": recall_score(y_test, prediction), "f1": f1_score(y_test, prediction)})
    smote_pipeline = ImbPipeline([("preprocessor", classifier_preprocessor()), ("smote", SMOTE(random_state=RANDOM_STATE)), ("model", RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE))])
    smote_pipeline.fit(X_train, y_train); prediction = smote_pipeline.predict(X_test)
    rows.append({"strategy": "SMOTE_train_only", "precision": precision_score(y_test, prediction), "recall": recall_score(y_test, prediction), "f1": f1_score(y_test, prediction)})
    result = pd.DataFrame(rows).set_index("strategy"); result.to_csv(ARTIFACTS / "imbalance_comparison.csv"); return result


def tune_and_regress(frame, X_train, X_test, y_train, y_test):
    grid = GridSearchCV(Pipeline([("preprocessor", classifier_preprocessor()), ("model", RandomForestClassifier(oob_score=True, bootstrap=True, random_state=RANDOM_STATE))]), {"model__n_estimators": [80, 120], "model__max_depth": [None, 6], "model__max_features": ["sqrt", "log2"]}, cv=3, scoring="f1", n_jobs=-1)
    grid.fit(X_train, y_train)
    best_pipeline = grid.best_estimator_; joblib.dump(best_pipeline, ARTIFACTS / "best_classifier_pipeline.joblib")
    reloaded = joblib.load(ARTIFACTS / "best_classifier_pipeline.joblib"); reloaded.predict(X_test.iloc[:2])
    oob_score = best_pipeline.named_steps["model"].oob_score_

    regression_features = ["age", "pclass", "sibsp", "parch", "sex", "embarked", "survived"]
    reg_x_train, reg_x_test, reg_y_train, reg_y_test = train_test_split(frame[regression_features], frame["fare"], test_size=0.2, random_state=RANDOM_STATE)
    reg_pipeline = Pipeline([("preprocessor", ColumnTransformer([("numeric", Pipeline([("imputer", __import__("sklearn").impute.SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), ["age", "pclass", "sibsp", "parch", "survived"]), ("categorical", Pipeline([("imputer", __import__("sklearn").impute.SimpleImputer(strategy="most_frequent")), ("encoder", OneHotEncoder(handle_unknown="ignore"))]), ["sex", "embarked"])])), ("model", LinearRegression())])
    reg_pipeline.fit(reg_x_train, reg_y_train); prediction = reg_pipeline.predict(reg_x_test); residuals = reg_y_test - prediction
    r2 = r2_score(reg_y_test, prediction); n, p = len(reg_y_test), reg_pipeline.named_steps["preprocessor"].transform(reg_x_test).shape[1]
    regression = {"MAE": mean_absolute_error(reg_y_test, prediction), "RMSE": mean_squared_error(reg_y_test, prediction) ** 0.5, "R2": r2, "Adjusted_R2": 1 - (1 - r2) * (n - 1) / (n - p - 1)}
    pd.DataFrame([regression]).to_csv(ARTIFACTS / "regression_metrics.csv", index=False)
    fig, ax = plt.subplots(); sns.scatterplot(x=prediction, y=residuals, ax=ax); ax.axhline(0, color="red"); ax.set(xlabel="Predicted fare", ylabel="Residual"); fig.tight_layout(); fig.savefig(ARTIFACTS / "regression_residuals.png"); plt.close(fig)
    return {"best_params": grid.best_params_, "oob_score": oob_score, "regression": regression}


def run():
    raw = load_once(); missing = profile(raw); cleaned = clean(raw, missing); eda = run_eda(cleaned)
    X_train, X_test, y_train, y_test, metrics, _ = evaluate_classifiers(cleaned)
    imbalance = imbalance_comparison(X_train, X_test, y_train, y_test)
    tuning = tune_and_regress(cleaned, X_train, X_test, y_train, y_test)
    comparison = metrics.reset_index().rename(columns={"model": "classifier"})
    for metric_name, value in tuning["regression"].items():
        comparison[f"regression_{metric_name}"] = value
    comparison.to_csv(ARTIFACTS / "model_comparison.csv", index=False)
    summary = {"missing_percentages": missing, "eda": eda, "class_balance": cleaned["survived"].value_counts(normalize=True).round(4).to_dict(), "classifier_metrics": metrics.to_dict(), "imbalance": imbalance.to_dict(), "tuning_regression": tuning}
    (ARTIFACTS / "run_summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    return summary


if __name__ == "__main__":
    run()
