from regtools.dataprep import _create_reg_df_y_x_and_dummies, _estimate_handling_robust_and_cluster
from regtools.models import get_model_class_by_string, _is_probit_str, _is_logit_str


def reg(df, yvar, xvars, robust=True, cluster=False, cons=True, fe=None, interaction_tuples=None,
        num_lags=0, lag_variables='xvars', lag_period_var='Date', lag_id_var='TICKER',
        lag_fill_method: str='ffill',
        model_type='OLS'):
    """
    Returns a fitted regression. Takes df, produces a regression df with no missing among needed
    variables, and fits a regression model. If robust is specified, uses heteroskedasticity-
    robust standard errors. If cluster is specified, calculated clustered standard errors
    by the given variable.

    Note: only specify at most one of robust and cluster.

    Required inputs:
    df: pandas dataframe containing regression data
    yvar: str, column name of outcome y variable
    xvars: list of strs, column names of x variables for regression

    Optional inputs:
    robust: bool, set to True to use heterskedasticity-robust standard errors
    cluster: False or list of strs, set to a column name to calculate standard errors within clusters
             given by unique values of given column name. set to multiple column names for multiway
             clustering following Cameron, Gelbach, and Miller (2011). NOTE: will get exponentially
             slower as more cluster variables are added
    cons: bool, set to False to not include a constant in the regression
    fe: None or str or list of strs. If a str or list of strs is passed, uses these categorical
    variables to construct dummies for fixed effects.
    interaction_tuples: tuple or list of tuples of column names to interact and include as xvars
    num_lags: int, Number of periods to lag variables. Setting to other than 0 will activate lags
    lag_variables: 'all', 'xvars', or list of strs of names of columns to lag for regressions.
    lag_period_var: str, only used if lag_variables is not None. name of column which
                    contains period variable for lagging
    lag_id_var: str, only used if lag_variables is not None. name of column which
                    contains identifier variable for lagging
    lag_fill_method: str, 'ffill' or 'bfill' for which method to use to fill in missing rows when
                     creating lag variables. See pandas.DataFrame.fillna for more details
    model_type: str, 'OLS', 'probit', or 'logit' for type of model

    Returns:
    If fe=None, returns statsmodels regression result
    if fe is not None, returns a tuple of (statsmodels regression result, dummy_cols_dict)
    """
    regdf, y, X, dummy_cols_dict, lag_variables = _create_reg_df_y_x_and_dummies(df, yvar, xvars, cluster=cluster,
                                                                                 cons=cons, fe=fe,
                                                                                 interaction_tuples=interaction_tuples, num_lags=num_lags,
                                                                                 lag_variables=lag_variables, lag_period_var=lag_period_var,
                                                                                 lag_id_var=lag_id_var,
                                                                                 fill_method=lag_fill_method)

    ModelClass = get_model_class_by_string(model_type)
    mod = ModelClass(y, X)

    if _is_probit_str(model_type) or _is_logit_str(model_type):
        fit_kwargs = dict(
            method='bfgs',
            maxiter=100
        )
    else:
        fit_kwargs = {}

    result = _estimate_handling_robust_and_cluster(regdf, mod, robust, cluster, **fit_kwargs)

    # Only return dummy_cols_dict when fe is active
    if fe is not None:
        result.dummy_cols_dict = dummy_cols_dict
    else:
        result.dummy_cols_dict = None

    if cluster:
        result.cluster_variables = cluster
    else:
        result.cluster_variables = None

    return result


