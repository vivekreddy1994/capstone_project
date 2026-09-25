# Titanic Analytics Pipeline

## Run

From the repository root:

```powershell
python -m pip install -r analytics/requirements.txt
python analytics/src/titanic_pipeline.py
```

The script calls `sns.load_dataset("titanic")` once and immediately writes `analytics/titanic.csv`. If the network is unavailable later, the same script reads that committed CSV fallback. All later cleaning, EDA, modeling, tuning, and regression use that one loaded/cleaned dataset.

## Cleaning and EDA

Measured missingness was: `age` 19.87%, `embarked` 0.22%, `deck` 77.22%, and `embark_town` 0.22%. The 5% to 30% rule imputes `age` with its median; the under-5% rule drops affected rows for `embarked` and `embark_town`; the over-30% `deck` column is dropped because it is too incomplete for reliable imputation. Numeric and categorical modeling preprocessing is separately fit only on the training split.

IQR outlier counts are 65 for `age` and 114 for `fare`. Fare is right-skewed because mean (32.10) > median (14.45) > mode (8.05). Survival is higher for females (0.7404) than males (0.1889), and decreases from first class (0.6262) to third class (0.2424). The sex-plus-class breakdown shows the strongest survival group is first-class females (0.9674), while third-class males are lowest (0.1354).

The correlation heatmap uses exactly `survived`, `pclass`, `age`, `sibsp`, `parch`, and `fare`; `adult_male` and `alone` are excluded. The two strongest absolute off-diagonal correlations are `pclass`/`fare` (-0.5482), showing higher class numbers associate with lower fares, and `sibsp`/`parch` (0.4145), showing family-group features tend to rise together. Z-score checks produce means approximately 0 and population standard deviations 1 for both `age` and `fare`.

Charts and their interpretations are generated in `analytics/artifacts/`. The age distribution chart shows a broad passenger-age mix, while its boxplot identifies the 65 IQR outliers; the fare distribution chart shows a long right tail, while its boxplot identifies 114 high-fare outliers. The survival-by-sex chart shows a large female advantage, and the survival-by-class chart shows survival falling from first to third class. The sex-and-class chart shows the interaction clearly: class matters within each sex, with first-class females highest and third-class males lowest. The fare-by-survival boxplot shows survivors generally paid more, while the age/fare scatterplot shows survival concentrated among higher-fare groups and younger passengers. Together they support the conclusion that sex and passenger class are the clearest survival separators, with fare acting as a class proxy.

## Modeling

The split is stratified because the target is imbalanced: 61.75% did not survive and 38.25% survived. The same 80/20 split is used for Logistic Regression, Decision Tree, and Random Forest. A `ColumnTransformer` imputes/scales numeric fields and imputes/one-hot-encodes `sex` and `embarked`, fit only through each training pipeline.

| Model | Accuracy | Precision | Recall | F1 | AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.8090 | 0.7833 | 0.6912 | 0.7344 | 0.8610 |
| Decision Tree | 0.7472 | 0.7347 | 0.5294 | 0.6154 | 0.8259 |
| Random Forest | 0.8034 | 0.7619 | 0.7059 | 0.7328 | 0.8225 |

The imbalance comparison shows baseline F1 0.7287, class-weight-balanced F1 0.7591, and train-only SMOTE F1 0.7591. Both balanced approaches improve recall from 0.6912 to 0.7647, so balanced weighting is the simpler deployment choice; SMOTE is applied only after preprocessing to the training fold. GridSearchCV selected `n_estimators=120`, `max_depth=None`, and `max_features="sqrt"`; the OOB score is 0.8087. The decision tree, confusion matrices, and ROC curves are saved as supporting artifacts.

The fare regression side-task reports MAE 21.10, RMSE 41.70, R2 0.3482, and adjusted R2 0.3091. The residual plot is included; its wider spread for high predicted fares indicates heteroscedasticity rather than constant random variance. `model_comparison.csv` keeps classifier metrics (`accuracy`, `precision`, `recall`, `f1`, `auc`) separate from regression metrics (`regression_MAE`, `regression_RMSE`, `regression_R2`, `regression_Adjusted_R2`). Logistic Regression is the deployment recommendation because it has the highest AUC (0.8610), highest accuracy (0.8090), and nearly the best F1 while remaining simpler and more interpretable than Random Forest. If recall is prioritized over simplicity, the balanced model is preferable because it catches more survivors.

The complete fitted classifier pipeline, including preprocessing and estimator, is saved at `analytics/artifacts/best_classifier_pipeline.joblib`. The script reloads it with `joblib.load` and predicts on raw test rows.
