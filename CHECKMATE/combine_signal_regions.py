
import pyhf
import numpy as np

pyhf.set_backend("numpy", precision="64b")

def compute_r_exp_cons_scaled(s0, ds0, b0, db0, lumi_factors,df):
    """
    Compute s95exp and r_exp_cons for a range of luminosity scaling factors.

    Args:
        s0 (float): Initial signal yield
        ds0 (float): Initial uncertainty on signal
        b0 (float): Initial background yield
        db0 (float): Initial uncertainty on background
        lumi_factors (list of float): Scaling factors for luminosity

    Returns:
        List of dicts with results for each luminosity factor
    """
    results = []

    for k in lumi_factors:
        s = k * s0
        ds = np.sqrt(k) * ds0
        b = k * b0
        db = np.sqrt(k) * db0

        spec = {
            "channels": [{
                "name": "signal_region",
                "samples": [
                    {
                        "name": "signal",
                        "data": [1.0],
                        "modifiers": [
                            {"name": "mu", "type": "normfactor", "data": None}
                        ]
                    },
                    {
                        "name": "background",
                        "data": [b],
                        "modifiers": [
                            {
                                "name": "bkg_unc",
                                "type": "normsys",
                                "data": {
                                    "hi": 1 + db / b,
                                    "lo": 1 - db / b
                                }
                            }
                        ]
                    }
                ]
            }]
        }

        model = pyhf.Model(spec, poi_name="mu")
        init_pars = model.config.suggested_init()
        par_bounds = model.config.suggested_bounds()
        par_bounds[0] = (0.0, 1000.0)

        asimov_data = model.expected_data(init_pars)
        mu_up = pyhf.infer.intervals.upper_limits.upper_limit(
            data=asimov_data,
            model=model,
            level=0.05,
            par_bounds=par_bounds
        )

        if isinstance(mu_up, (list, tuple, np.ndarray)):
            mu_up = mu_up[0]

        s95exp = mu_up
        r_exp_cons = (s - 1.64 *df* ds) / s95exp

        results.append({
            "luminosity_factor": k,
            "s": s,
            "ds": ds,
            "b": b,
            "db": db,
            "s95exp": s95exp,
            "r_exp_cons": r_exp_cons
        })

    return results


def combine_signal_regions(signal_regions, lumi_factors):
    """
    Combine multiple orthogonal signal regions by summing signal/background yields and variances.

    Args:
        signal_regions (list of dict): Each dict must contain 's0', 'ds0', 'b0', 'db0'
        lumi_factors (list of float): Luminosity scaling factors

    Returns:
        List of dicts with combined results per luminosity factor
    """
    combined_results = []

    for k in lumi_factors:
        total_s = 0.0
        total_var_s = 0.0
        total_b = 0.0
        total_var_b = 0.0

        for sr in signal_regions:
            s = k * sr['s0']
            ds = np.sqrt(k) * sr['ds0']
            b = k * sr['b0']
            db = np.sqrt(k) * sr['db0']

            total_s += s
            total_var_s += ds**2
            total_b += b
            total_var_b += db**2

        combined_ds = np.sqrt(total_var_s)
        combined_db = np.sqrt(total_var_b)

        result = compute_r_exp_cons_scaled(
            s0=total_s,
            ds0=combined_ds,
            b0=total_b,
            db0=combined_db,
            lumi_factors=[1],
	    df=0
        )[0]

        result['luminosity_factor'] = k
        combined_results.append(result)

    return combined_results


# === Example usage ===
if __name__ == "__main__":
    signal_regions = [
        {'s0': 50, 'ds0': 0.1 , 'b0': 100, 'db0': 0},
        {'s0': 50, 'ds0': 0.05, 'b0': 100, 'db0': 0}
    ]

    lumi_factors = [1,4]

    combined_results = combine_signal_regions(signal_regions, lumi_factors)

    print("\n===== Combined SRs Luminosity Scaling Study =====")
    for res in combined_results:
        print(f"Luminosity x{res['luminosity_factor']:>2}: "
              f"s95exp = {res['s95exp']:.4f}, r_exp_cons = {res['r_exp_cons']:.5f}")
    print("=================================================\n")

 
    signal_regions = [
        {'s0': 50, 'ds0': 0.1 , 'b0': 100, 'db0': 0}
     ]

    lumi_factors = [1,4]

    combined_results = combine_signal_regions(signal_regions, lumi_factors)

    print("\n===== Combined SRs Luminosity Scaling Study =====")
    for res in combined_results:
        print(f"Luminosity x{res['luminosity_factor']:>2}: "
              f"s95exp = {res['s95exp']:.4f}, r_exp_cons = {res['r_exp_cons']:.5f}")
    print("=================================================\n")



