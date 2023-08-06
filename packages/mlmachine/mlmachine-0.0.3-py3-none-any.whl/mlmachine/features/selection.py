import matplotlib.pyplot as plt

from time import gmtime, strftime

import numpy as np
import pandas as pd

from sklearn.feature_selection import (
    f_classif,
    f_regression,
    VarianceThreshold,
    SelectFromModel,
    SelectKBest,
)
from sklearn.model_selection import (
    KFold,
    train_test_split,
    GridSearchCV,
    StratifiedKFold,
    cross_val_score,
    RandomizedSearchCV,
    cross_validate,
)

from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    AdaBoostClassifier,
    ExtraTreesClassifier,
    IsolationForest,
    RandomForestRegressor,
    GradientBoostingRegressor,
    ExtraTreesRegressor,
    AdaBoostRegressor,
)
from sklearn.linear_model import (
    Lasso,
    Ridge,
    ElasticNet,
    LinearRegression,
    LogisticRegression,
    SGDRegressor,
)
from sklearn.feature_selection import RFE
from sklearn.kernel_ridge import KernelRidge
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.svm import SVC, SVR
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier

from xgboost import XGBClassifier, XGBRegressor
from lightgbm import LGBMClassifier, LGBMRegressor
import catboost

from prettierplot.plotter import PrettierPlot
from prettierplot import style


from ..model.tune.bayesian_optim_search import BasicModelBuilder


class FeatureSelector:
    """
    documentation:
        description:
            evaluate feature importance using several different feature selection techniques,
            including f_score, variance, recursive feature selection, and correlation to target
            on a list of estimators. also includes methods for performing corss_validation and
            visualization of the results.p
        parameters:
            data : pandas DataFrame, default=None
                pandas DataFrame containing independent variables. if left as none,
                the feature dataset provided to machine during instantiation is used.
            target : Pandas Series, default=None
                Pandas Series containing dependent target variable. if left as none,
                the target dataset provided to machine during instantiation is used.
            estimators : list of strings or sklearn api objects.
                    list of estimators to be used.
            classification : bool, default=True
                conditional controlling whether object is informed that the supervised learning
                task is a classification task.
    """

    def __init__(self, data, target, estimators, classification=True):
        self.data = data
        self.target = target
        self.estimators = estimators
        self.classification = classification

    def feature_selector_suite(self, rank=False, add_stats=False, n_jobs=1, save_to_csv=False):
        """
        documentation:
            description:
                run all feature selections processes and aggregate results. calculate summary
                statistics on results.
            parameters:
                rank : bool, default=False
                    conditional controlling whether to overwrite values with rank of values.
                add_stats : bool, default=True
                    add row-wise summary statistics for feature importance ranking columns.
                    requires columns to be ranked in ascending or descending order, which
                    enforces consistent directionality in assigning importance, and normalize
                    the scale of the feature importance values. Ignored if one feature
                    importance column is provided. If raw feature importance values are provided
                    values are converted to ranks.
                n_jobs : int, default=1
                    number of works to deploy upon execution, if applicable. if estimator does not
                    have an n_jobs parameter, this is ignored.
                save_to_csv : bool, default=True
                    conditional controlling whethor or not the feature selection summary results
                    are saved to a csv file.
        """
        # run individual top feature processes
        self.results_variance = self.feature_selector_variance(rank=rank)
        self.results_importance = self.feature_selector_importance(rank=rank, n_jobs=n_jobs)
        self.results_rfe = self.feature_selector_rfe(n_jobs=n_jobs)
        self.results_corr = self.feature_selector_corr(rank=rank)
        if self.classification:
            self.results_f_score = self.feature_selector_f_score_class(rank=rank)
        else:
            self.results_f_score = self.feature_selector_f_score_reg(rank=rank)

        # combine results into single summary table
        results = [
            self.results_f_score,
            self.results_variance,
            self.results_corr,
            self.results_rfe,
            self.results_importance,
        ]
        feature_selector_summary = pd.concat(results, join="inner", axis=1)

        if add_stats:
            feature_selector_summary = self.feature_selector_stats(feature_selector_summary)

        if save_to_csv:
            feature_selector_summary.to_csv(
                "feature_selection_summary_{}.csv".format(
                    strftime("%y%m%d%H%M", gmtime())
                ),
                columns=feature_selector_summary.columns,
            )
        return feature_selector_summary

    def feature_selector_f_score_class(self, rank=False):
        """
        documentation:
            description:
                for each feature, calculate f_values and p_values in the context of a
                classification problem.
            parameters
                rank : bool, default=False
                    conditional controlling whether to overwrite values with rank of values.
        """
        # calculate f_values and p_values
        univariate = f_classif(self.data, self.target)

        # parse data into dictionary
        feature_dict = {}
        feature_dict["f_value"] = univariate[0]
        feature_dict["p_value"] = univariate[1]

        # load dictionary into pandas DataFrame and rank values
        feature_selector_summary = pd.DataFrame(data=feature_dict, index=self.data.columns)

        # overwrite values with rank
        if rank:
            feature_selector_summary = self.apply_ranks(feature_selector_summary)
        return feature_selector_summary

    def feature_selector_f_score_reg(self, rank=False):
        """
        documentation:
            description:
                for each feature, calculate f_values and p_values in the context of a
                regression problem.
            parameters
                rank : bool, default=False
                    conditional controlling whether to overwrite values with rank of values.
        """
        # calculate f_values and p_values
        univariate = f_regression(self.data, self.target)

        # parse data into dictionary
        feature_dict = {}
        feature_dict["f_value"] = univariate[0]
        feature_dict["p_value"] = univariate[1]

        # load dictionary into pandas DataFrame and rank values
        feature_selector_summary = pd.DataFrame(data=feature_dict, index=self.data.columns)

        # overwrite values with rank
        if rank:
            feature_selector_summary = self.apply_ranks(feature_selector_summary)
        return feature_selector_summary

    def feature_selector_variance(self, rank=False):
        """
        documentation:
            description:
                for each feature, calculate variance.
            parameters
                rank : bool, default=False
                    conditional controlling whether to overwrite values with rank of values.
        """
        # calculate variance
        var_importance = VarianceThreshold()
        var_importance.fit(self.data)

        variance = "variance{}".format("_rank" if rank else "")

        # load data into pandas DataFrame and rank values
        feature_selector_summary = pd.DataFrame(
            var_importance.variances_, index=self.data.columns, columns=[variance]
        )

        # overwrite values with rank
        if rank:
            feature_selector_summary = self.apply_ranks(feature_selector_summary)

        return feature_selector_summary

    def feature_selector_importance(self, rank=False, add_stats=False, n_jobs=1):
        """
        documentation:
            description:
                for each estimator, for each feature, calculate feature importance.
            parameters
                rank : bool, default=False
                    conditional controlling whether to overwrite values with rank of values.
                add_stats : bool, default=True
                    add row-wise summary statistics for feature importance ranking columns.
                    requires columns to be ranked in ascending or descending order, which
                    enforces consistent directionality in assigning importance, and normalize
                    the scale of the feature importance values. Ignored if one feature
                    importance column is provided. If raw feature importance values are provided
                    values are converted to ranks.
                n_jobs : int, default=1
                    number of works to deploy upon execution, if applicable. if estimator does not
                    have an n_jobs parameter, this is ignored.
        """
        #
        feature_dict = {}
        for estimator in self.estimators:
            model = BasicModelBuilder(estimator=estimator, n_jobs=n_jobs)

            # estimator name
            if model.estimator.__module__.split(".")[1] == "sklearn":
                estimator_module = model.estimator.__module__.split(".")[0]
            else:
                estimator_module = model.estimator.__module__.split(".")[1]

            estimator_name =  model.estimator.__name__ + "_feature_importance"

            # build dict
            feature_dict[estimator_name] = model.feature_importances(self.data.values, self.target)

        feature_selector_summary = pd.DataFrame(feature_dict, index=self.data.columns)

        # overwrite values with rank
        if rank:
            feature_selector_summary = self.apply_ranks(feature_selector_summary)

        # add summary statistics columns
        if add_stats:
            feature_selector_summary = self.feature_selector_stats(feature_selector_summary)

        return feature_selector_summary

    def feature_selector_rfe(self, add_stats=False, n_jobs=1):
        """
        documentation:
            description:
                for each estimator, recursively remove features one at a time, capturing
                the step in which each feature is removed.
            parameters:
                add_stats : bool, default=True
                    add row-wise summary statistics for feature importance ranking columns.
                    requires columns to be ranked in ascending or descending order, which
                    enforces consistent directionality in assigning importance, and normalize
                    the scale of the feature importance values. Ignored if one RFE rank
                    column is provided.
                n_jobs : int, default=1
                    number of works to deploy upon execution, if applicable. if estimator does not
                    have an n_jobs parameter, this is ignored.
        """
        #
        feature_dict = {}
        for estimator in self.estimators:
            model = BasicModelBuilder(estimator=estimator, n_jobs=n_jobs)

            # estimator name
            if model.estimator.__module__.split(".")[1] == "sklearn":
                estimator_module = model.estimator.__module__.split(".")[0]
            else:
                estimator_module = model.estimator.__module__.split(".")[1]

            estimator_name =  model.estimator.__name__ + "_rfe_rank"

            # recursive feature selection
            rfe = RFE(estimator=model.model, n_features_to_select=1, step=1, verbose=0)
            rfe.fit(self.data, self.target)
            feature_dict[estimator_name] = rfe.ranking_

        feature_selector_summary = pd.DataFrame(feature_dict, index=self.data.columns)

        # add summary statistics columns
        if add_stats:
            feature_selector_summary = self.feature_selector_stats(feature_selector_summary)

        return feature_selector_summary

    def feature_selector_corr(self, rank=False):
        """
        documentation:
            description:
                for each feature, calculate absolute correlation coefficient relative to
                target dataset.
            parameters:
                rank : bool, default=False
                    conditional controlling whether to overwrite values with rank of values.
        """
        # calculate absolute correlation coefficients relative to target
        feature_selector_summary = self.data.merge(self.target, left_index=True, right_index=True)

        correlation_to_target = "correlation_to_target"

        feature_selector_summary = pd.DataFrame(feature_selector_summary.corr().abs()[self.target.name])
        feature_selector_summary = feature_selector_summary.rename(columns={self.target.name: correlation_to_target})

        feature_selector_summary = feature_selector_summary.sort_values(correlation_to_target, ascending=False)
        feature_selector_summary = feature_selector_summary.drop(self.target.name, axis=0)

        # overwrite values with rank
        # higher values are better and are given lower number values for ranks
        if rank:
            feature_selector_summary = self.apply_ranks(feature_selector_summary)

        return feature_selector_summary

    def apply_ranks(self, feature_selector_summary):
        """
        documentation:
            description:
                apply ascending or descending ranking on feature importance values.
            parameters:
                feature_selector_summary : Pandas DataFrame
                    Pandas DataFrame with an index corresponding to feature names and columns
                    corresponding to feature importance values.
        """
        ascending_rank = ["p_value","rfe"]
        descending_rank = ["feature_importance","f_value","variance","correlation_to_target"]

        # capture column to rank in ascending order
        apply_ascending_rank = []
        for column in ascending_rank:
            apply_ascending_rank.extend([s for s in feature_selector_summary.columns if column in s])

        # overwrite values with ascending rank
        for column in apply_ascending_rank:
            feature_selector_summary[column] = feature_selector_summary[column].rank(ascending=True, method="max")
            # feature_selector_summary[column] = feature_selector_summary[column].astype("int")
            feature_selector_summary = feature_selector_summary.rename({column: column + "_rank"}, axis=1)

        # capture column to rank in descending order
        apply_descending_rank = []
        for column in descending_rank:
            apply_descending_rank.extend([s for s in feature_selector_summary.columns if column in s])

        # overwrite values with descending rank
        for column in apply_descending_rank:
            feature_selector_summary[column] = feature_selector_summary[column].rank(ascending=False, method="max")
            # feature_selector_summary[column] = feature_selector_summary[column].astype("int")
            feature_selector_summary = feature_selector_summary.rename({column: column + "_rank"}, axis=1)
        return feature_selector_summary

    def feature_selector_stats(self, feature_selector_summary):
        """
        documentation:
            description:
                add row-wise summary statistics for feature importance ranking columns. if data
                provided includes raw feature importance values, ranking will be applied
                automatically.
            parameters:
                feature_selector_summary : Pandas DataFrame
                    Pandas DataFrame with an index corresponding to feature names and columns
                    corresponding to feature importance values or feature importance rankings.
        """
        # apply ranking if needed
        if not feature_selector_summary.columns.str.endswith("_rank").sum() == feature_selector_summary.shape[1]:
            feature_selector_summary = self.apply_ranks(feature_selector_summary)

        # add summary stats
        feature_selector_summary.insert(
            loc=0, column="average", value=feature_selector_summary.mean(axis=1)
        )
        feature_selector_summary.insert(
            loc=1,
            column="stdev",
            value=feature_selector_summary.iloc[:, 1:].std(axis=1),
        )
        feature_selector_summary.insert(
            loc=2,
            column="best",
            value=feature_selector_summary.iloc[:, 2:].min(axis=1),
        )
        feature_selector_summary.insert(
            loc=3,
            column="worst",
            value=feature_selector_summary.iloc[:, 3:].max(axis=1),
        )
        feature_selector_summary = feature_selector_summary.sort_values("average")
        return feature_selector_summary

    def feature_selector_cross_val(self, scoring, feature_selector_summary=None, estimators=None,
                                    n_folds=3, step=1, n_jobs=4, verbose=False, save_to_csv=False):
        """
        documentation:
            description:
                perform cross_validation for each estimator, for progressively smaller sets of features. the list
                of features is reduced by one feature on each pass. the feature removed is the least important
                feature of the remaining set. calculates both the training and test performance.
            parameters:
                scoring : list of strings
                    list containing strings for one or more performance scoring metrics.
                feature_selector_summary : pandas DataFrame or str, default=None
                    pandas DataFrame, or str of csv file location, containing summary of feature_selector_suite results.
                    if none, use object's internal attribute specified during instantiation.
                estimators : list of strings or sklearn api objects, default=None
                    list of estimators to be used. if none, use object's internal attribute specified during instantiation.
                n_folds : int, default=3
                    number of folds to use in cross validation.
                step : int, default=1
                    number of features to remove per iteration.
                n_jobs : int, default=4
                    number of works to use when training the model. this parameter will be
                    ignored if the model does not have this parameter.
                verbose : bool, default=False
                    conditional controlling whether each estimator name is printed prior to cross_validation.
                save_to_csv : bool, default=True
                    conditional controlling whethor or not the feature selection summary results
                    are saved to a csv file.
        """
        # load results summary if needed
        if isinstance(feature_selector_summary, str):
            feature_selector_summary = pd.read_csv(
                feature_selector_summary, index_col=0
            )
        elif isinstance(feature_selector_summary, pd.core.frame.DataFrame):
            feature_selector_summary = feature_selector_summary
        elif feature_selector_summary is None:
            raise AttributeError(
                "no feature_selector_summary detected. execute one of the feature selector methods or load from .csv"
            )

        # add summary stats if needed
        if not "average" in feature_selector_summary.columns:
            feature_selector_summary = self.feature_selector_stats(feature_selector_summary)

        # load estimators if needed
        if estimators is None:
            estimators = self.estimators

        # create empty dictionary for capturing one DataFrame for each estimator
        self.cv_summary = pd.DataFrame(
            columns=[
                "estimator",
                "training score",
                "validation score",
                "scoring",
                "features dropped",
            ]
        )

        # perform cross validation for all estimators for each diminishing set of features
        row_ix = 0

        for estimator in estimators:

            if verbose:
                print(estimator)

            # instantiate default model and create empty DataFrame for capturing scores
            model = BasicModelBuilder(estimator=estimator, n_jobs=n_jobs)
            cv = pd.DataFrame(
                columns=[
                    "estimator",
                    "training score",
                    "validation score",
                    "scoring",
                    "features dropped",
                ]
            )

            # estimator name
            if model.estimator.__module__.split(".")[1] == "sklearn":
                estimator_module = model.estimator.__module__.split(".")[0]
            else:
                estimator_module = model.estimator.__module__.split(".")[1]

            estimator_class = model.estimator.__name__
            estimator_name = estimator_class

            # iterate through scoring metrics
            for metric in scoring:

                step_increment = 0

                # iterate through each set of features
                for i in np.arange(0, feature_selector_summary.shape[0], step):

                    # collect names of top columns
                    if i == 0:
                        top = feature_selector_summary.sort_values("average").index
                    else:
                        top = feature_selector_summary.sort_values("average").index[:-i]

                    # custom metric handling
                    if metric == "root_mean_squared_error":
                        metric = "neg_mean_squared_error"
                        score_transform = "rmse"
                    elif metric == "root_mean_squared_log_error":
                        metric = "neg_mean_squared_log_error"
                        score_transform = "rmsle"
                    else:
                        score_transform = metric

                    scores = cross_validate(
                        estimator=model.model,
                        X=self.data[top],
                        y=self.target,
                        cv=n_folds,
                        scoring=metric,
                        return_train_score=True,
                    )

                    # custom metric handling
                    if score_transform == "rmse":
                        training = np.mean(np.sqrt(np.abs(scores["train_score"])))
                        validation = np.mean(np.sqrt(np.abs(scores["test_score"])))
                        metric = "root_mean_squared_error"
                    elif score_transform == "rmsle":
                        training = np.mean(np.sqrt(np.abs(scores["train_score"])))
                        validation = np.mean(np.sqrt(np.abs(scores["test_score"])))
                        metric = "root_mean_squared_log_error"
                    else:
                        training = np.mean(scores["train_score"])
                        validation = np.mean(scores["test_score"])

                    # append results
                    cv.loc[row_ix] = [
                        estimator_name,
                        training,
                        validation,
                        metric,
                        step_increment,
                    ]
                    step_increment += step
                    row_ix += 1

            # capturing results DataFrame associated with estimator
            self.cv_summary = self.cv_summary.append(cv)

        if save_to_csv:
            self.cv_summary.to_csv(
                "cv_summary_{}.csv".format(strftime("%y%m%d%H%M", gmtime())),
                columns=self.cv_summary.columns,
                index_label="index",
            )

        return self.cv_summary

    def feature_selector_results_plot(self, scoring, cv_summary=None, feature_selector_summary=None, top_sets=0,
                                    show_features=False, show_scores=None, marker_on=True, title_scale=0.7,):
        """
        documentation:
            description:
                for each estimator, visualize the training and validation performance
                for each feature set.
            parameters:
                scoring : string
                    scoring metric to visualize.
                cv_summary : pandas DataFrame or str, default=None
                    pandas DataFrame, or str of csv file location, containing cross_validation results.
                    if none, use object's internal attribute specified during instantiation.
                feature_selector_summary : pandas DataFrame or str, default=None
                    pandas DataFrame, or str of csv file location, containing summary of feature_selector_suite results.
                    if none, use object's internal attribute specified during instantiation.
                top_sets : int, default=5
                    number of rows to display of the performance summary table
                show_features : bool, default=False
                    conditional controlling whether to print feature set for best validation
                    score.
                show_scores : int or none, default=None
                    display certain number of top features. if none, display nothing. if int, display
                    the specified number of features as a pandas DataFrame.
                marker_on : bool, default=True
                    conditional controlling whether to display marker for each individual score.
                title_scale : float, default=1.0
                    controls the scaling up (higher value) and scaling down (lower value) of the size of
                    the main chart title, the x_axis title and the y_axis title.
        """
        # load results summary if needed
        if isinstance(feature_selector_summary, str):
            feature_selector_summary = pd.read_csv(
                feature_selector_summary, index_col=0
            )
        elif isinstance(feature_selector_summary, pd.core.frame.DataFrame):
            feature_selector_summary = feature_selector_summary
        elif feature_selector_summary is None:
            raise AttributeError(
                "no feature_selector_summary detected. either execute method feature_selector_suite or load from .csv"
            )

        # load cv summary if needed
        if isinstance(cv_summary, str):
            cv_summary = pd.read_csv(cv_summary, index_col=0)
        elif isinstance(cv_summary, pd.core.frame.DataFrame):
            cv_summary = cv_summary
        elif cv_summary is None:
            raise AttributeError(
                "no cv_summary detected. either execute method feature_selector_cross_val or load from .csv"
            )

        # add summary stats if needed
        if not "average" in feature_selector_summary.columns:
            feature_selector_summary = self.feature_selector_stats(feature_selector_summary)

        for estimator in cv_summary["estimator"].unique():
            cv = cv_summary[
                (cv_summary["scoring"] == scoring)
                & (cv_summary["estimator"] == estimator)
            ]

            total_features = feature_selector_summary.shape[0]
            iters = cv.shape[0]
            step = np.ceil(total_features / iters)

            cv.set_index(
                keys=np.arange(0, cv.shape[0] * step, step, dtype=int), inplace=True
            )

            if show_scores is not None:
                display(cv[:show_scores])

            # capture best iteration's feature drop count and performance score
            if scoring in ["root_mean_squared_error", "root_mean_squared_log_error"]:
                sort_order = True
            else:
                sort_order = False

            num_dropped = cv.sort_values(["validation score"], ascending=sort_order)[
                :1
            ]["features dropped"].values[0]
            score = np.round(
                cv.sort_values(["validation score"], ascending=sort_order)[
                    "validation score"
                ][:1].values[0],
                5,
            )

            # display performance for the top n feature sets
            if top_sets > 0:
                display(
                    cv.sort_values(["validation score"], ascending=sort_order)[
                        :top_sets
                    ]
                )
            if show_features:
                if num_dropped > 0:
                    features = feature_selector_summary.shape[0] - num_dropped
                    features_used = (
                        feature_selector_summary.sort_values("average")
                        .index[:features]
                        .values
                    )
                else:
                    features_used = feature_selector_summary.sort_values(
                        "average"
                    ).index.values
                print(features_used)

            # create multi_line plot
            p = PrettierPlot()
            ax = p.make_canvas(
                title="{}\nBest validation {} = {}\nFeatures dropped = {}".format(
                    estimator, scoring, score, num_dropped
                ),
                x_label="features removed",
                y_label=scoring,
                y_shift=0.4 if len(scoring) > 18 else 0.57,
                title_scale=title_scale,
            )

            p.multi_line(
                x=cv.index,
                y=["training score", "validation score"],
                label=["training score", "validation score"],
                df=cv,
                y_units="fff",
                marker_on=marker_on,
                bbox=(1.3, 0.9),
                ax=ax,
            )
            plt.show()

    def create_cross_val_features_df(self, scoring, cv_summary=None, feature_selector_summary=None):
        """
        documentation:
            description:
                for each estimator, visualize the training and validation performance
                for each feature set.
            parameters:
                scoring : string
                    scoring metric to visualize.
                cv_summary : pandas DataFrame or str, default=None
                    pandas DataFrame, or str of csv file location, containing cross_validation results.
                    if none, use object's internal attribute specified during instantiation.
                feature_selector_summary : pandas DataFrame or str, default=None
                    pandas DataFrame, or str of csv file location, containing summary of feature_selector_suite results.
                    if none, use object's internal attribute specified during instantiation.
        """
        # load results summary if needed
        if isinstance(feature_selector_summary, str):
            feature_selector_summary = pd.read_csv(
                feature_selector_summary, index_col=0
            )
        elif isinstance(feature_selector_summary, pd.core.frame.DataFrame):
            feature_selector_summary = feature_selector_summary
        elif feature_selector_summary is None:
            raise AttributeError(
                "no feature_selector_summary detected. either execute method feature_selector_suite or load from .csv"
            )

        # load cv summary if needed
        if isinstance(cv_summary, str):
            cv_summary = pd.read_csv(cv_summary, index_col=0)
        elif isinstance(cv_summary, pd.core.frame.DataFrame):
            cv_summary = cv_summary
        elif cv_summary is None:
            raise AttributeError(
                "no cv_summary detected. either execute method feature_selector_suite or load from .csv"
            )

        # add summary stats if needed
        if not "average" in feature_selector_summary.columns:
            feature_selector_summary = self.feature_selector_stats(feature_selector_summary)

        # create empty DataFrame with feature names as index
        self.cross_val_features_df = pd.DataFrame(index=feature_selector_summary.index)

        # iterate through estimators
        for estimator in cv_summary["estimator"].unique():
            cv = cv_summary[
                (cv_summary["scoring"] == scoring)
                & (cv_summary["estimator"] == estimator)
            ]
            cv = cv.reset_index(drop=True)

            # capture best iteration's feature drop count
            if scoring in ["root_mean_squared_error", "root_mean_squared_log_error"]:
                sort_order = True
            else:
                sort_order = False

            num_dropped = cv.sort_values(["validation score"], ascending=sort_order)[
                :1
            ]["features dropped"].values[0]
            if num_dropped > 0:
                features = feature_selector_summary.shape[0] - num_dropped
                features_used = (
                    feature_selector_summary.sort_values("average")
                    .index[:features]
                    .values
                )
            else:
                features_used = feature_selector_summary.sort_values(
                    "average"
                ).index.values

            # create column for estimator and populate with marker
            self.cross_val_features_df[estimator] = np.nan
            self.cross_val_features_df[estimator].loc[features_used] = "x"

        # add counter and fill na_ns
        self.cross_val_features_df["count"] = self.cross_val_features_df.count(axis=1)
        self.cross_val_features_df = self.cross_val_features_df.fillna("")

        # add numberal index starting at 1
        self.cross_val_features_df = self.cross_val_features_df.reset_index()
        self.cross_val_features_df.index = np.arange(
            1, len(self.cross_val_features_df) + 1
        )
        self.cross_val_features_df = self.cross_val_features_df.rename(
            columns={"index": "feature"}
        )
        return self.cross_val_features_df

    def create_cross_val_features_dict(self, cross_val_features_df=None):
        """
        documentation:
            description:
                for each estimator, visualize the training and validation performance
                for each feature set.
            parameters:
                cross_val_features_df : pandas DataFrame, default=None
                    pandas DataFrame, or str of csv file location, containing summary of features used
                    in each estimator to achieve best validation score. if none, use object's internal
                    attribute specified during instantiation.
        """
        # load results summary if needed
        if isinstance(cross_val_features_df, str):
            cross_val_features_df = pd.read_csv(cross_val_features_df, index_col=0)
        elif isinstance(cross_val_features_df, pd.core.frame.DataFrame):
            cross_val_features_df = cross_val_features_df
        elif cross_val_features_df is None:
            raise AttributeError(
                "no cross_val_features_df detected. either execute method create_cross_val_features_df or load from .csv"
            )

        # create empty dict with feature names as index
        self.cross_val_features_dict = {}

        cross_val_features_df = cross_val_features_df.set_index("feature")
        cross_val_features_df = cross_val_features_df.drop("count", axis=1)

        # iterate through estimators
        for estimator in cross_val_features_df.columns:
            self.cross_val_features_dict[estimator] = cross_val_features_df[
                cross_val_features_df[estimator] == "x"
            ][estimator].index

        return self.cross_val_features_dict
