from kts.modelling.mixins import MultiClassifierMixin

try:
    from xgboost import XGBClassifier as _XGBC

    class XGBClassifier(MultiClassifierMixin, _XGBC):
        """ """

        short_name = "xgb"
        tracked_params = [
            "base_score",
            "booster",
            "colsample_bylevel",
            "colsample_bytree",
            "gamma",
            "learning_rate",
            "max_delta_step",
            "max_depth",
            "min_child_weight",
            "missing",
            "n_estimators",
            "objective",
            "reg_alpha",
            "reg_lambda",
            "scale_pos_weight",
            "subsample",
        ]

except ImportError:
    pass

try:
    from lightgbm import LGBMClassifier as _LGBMC

    class LGBMClassifier(MultiClassifierMixin, _LGBMC):
        """ """

        short_name = "lgb"
        tracked_params = [
            "class_weight",
            "boost",
            "min_data_in_leaf",
            "bagging_freq",
            "subsample_freq",
            "bagging_fraction",
            "learning_rate",
            "reg_lambda",
            "feature_fraction",
            "min_sum_hessian_in_leaf",
            "boosting_type",
            "subsample_for_bin",
            "reg_alpha",
            "tree_learner",
            "colsample_bytree",
            "min_child_weight",
            "min_child_samples",
            "subsample",
            "max_depth",
            "boost_from_average",
            "num_leaves",
            "objective",
            "n_estimators",
            "min_split_gain",
        ]

except ImportError:
    pass

try:
    from catboost import CatBoostClassifier as _CBC

    class CatBoostClassifier(MultiClassifierMixin, _CBC):
        """ """

        short_name = "cb"
        tracked_params = [
            "iterations",
            "learning_rate",
            "l2_leaf_reg",
            "bootstrap_type",
            "bagging_temperature",
            "depth",
            "one_hot_max_size",
            "leaf_estimation_method",
            "nan_mode",
            "feature_border_type",
            "border_count",
            "max_depth",
            "colsample_bylevel",
            "eval_metric",
        ]

except ImportError:
    pass

from sklearn.ensemble import RandomForestClassifier as _RFC


class RandomForestClassifier(MultiClassifierMixin, _RFC):
    """ """

    short_name = "rf"
    tracked_params = [
        "bootstrap",
        "class_weight",
        "criterion",
        "max_depth",
        "max_features",
        "max_leaf_nodes",
        "min_impurity_decrease",
        "min_impurity_split",
        "min_samples_leaf",
        "min_samples_split",
        "min_weight_fraction_leaf",
        "n_estimators",
        "oob_score",
    ]


from sklearn.linear_model import LogisticRegression as _LR


class LogisticRegression(MultiClassifierMixin, _LR):
    """ """

    short_name = "lr"
    tracked_params = ["C", "penalty", "fit_intercept", "class_weight"]
