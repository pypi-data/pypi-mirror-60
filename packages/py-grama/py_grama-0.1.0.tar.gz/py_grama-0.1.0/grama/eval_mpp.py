__all__ = []

## Most probable point (MPP) search functions
# --------------------------------------------------
@curry
def eval_pma(
        model,
        beta=None,
        con=0.95,
        out="lim",
        df_det=None,
        df_stat=None,
        eval_grad=None
):
    """Performance Measure Approach for reliability analysis

    Perform a Performance Measure Approach (PMA) reliability analysis to
    determine the relevant limit-state quantiles for the given reliability
    index.

    Args:
        model (gr.Model): Model to evaluate
        beta (numeric): Target reliability index;
            Probability of Failure = norm.cdf(-beta)
        con (numeric): Confidence level; only for MIB
        out (array-like of strings or string): List of outputs to optimize;
            value "lim" will select all outputs with "g_" prefix
        df_det (DataFrame): Deterministic levels for evaluation; use "nom"
            for nominal deterministic levels
        df_stat (DataFrame or None): Covariance matrix for margin estimation
            using the Margin in Beta (MIB) approach

    Returns:
        DataFrame: Deterministic variable levels with desired output quantiles

    References:

    """
    if out == "lim":
        out = list(filter(
            lambda s: s[:2] == "g_",
            model.out
        ))

    ## Check invariants
    if not set(out).issubset(set(model.out)):
        raise ValueError("out must be subset of md.out or 'lim'")

    ## TODO
