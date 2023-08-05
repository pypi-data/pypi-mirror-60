"""
High-level tools for running regressions. Handles fixed effects, 2+ way clustering, hypothesis testing,
lagged variables, differenced variables, interaction effects, iteration tools, and producing summaries for a
variety of models including OLS, Logit, Probit, Quantile, and Fama-Macbeth.
"""
from .iter import (
    reg_for_each_combo,
    reg_for_each_xvar_set,
    reg_for_each_combo_select_and_produce_summary,
    reg_for_each_xvar_set_and_produce_summary,
    reg_for_each_yvar,
    reg_for_each_yvar_and_produce_summary,
    reg_for_each_lag,
    reg_for_each_lag_and_produce_summary
)
from .reg import reg
from .summarize import produce_summary
from .select import select_models
from .args import RegressionSetArgs

