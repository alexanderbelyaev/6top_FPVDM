import pyhf
import numpy as np

pyhf.set_backend("numpy", precision="64b")

# CheckMATE .txt input values
s = 5.2865
ds = 0.3766
b = 2.8
db = 0.9

"""

# Use dummy signal yield = 1.0; actual scaling done later
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

# Asimov dataset using nominal values
init_pars = model.config.suggested_init()
asimov_data = model.expected_data(init_pars)

# ---- Specify bounds to avoid ValueError ----
# Use wide bounds so that fitting succeeds
par_bounds = model.config.suggested_bounds()
par_bounds[0] = (0.0, 30.0)  # POI 'mu' bound

# Compute upper limit on mu at 95% CL with specified bounds
mu_up = pyhf.infer.intervals.upper_limits.upper_limit(
    data=asimov_data,
    model=model,
    level=0.05,
    par_bounds=par_bounds
)

if isinstance(mu_up, (list, tuple, np.ndarray)):
    mu_up = mu_up[0]

# Compute s95exp and CheckMATE-style r-value (conservative)
s95exp = mu_up
r_exp_cons = (s - 1.64*ds) / s95exp

# ---- Output ----
print("===== Reproducing CheckMATE-style r-value =====")
print(f"Signal (s)              = {s:.4f}")
print(f"Uncertainty on s (ds)   = {ds:.4f}")
print(f"Background (b)          = {b:.4f}")
print(f"Uncertainty on b (db)   = {db:.4f}")
print()
print(f"s95exp (from pyhf)      = {s95exp:.4f}")
print(f"r_exp_cons              = {r_exp_cons:.5f}")
print("===============================================")

"""

def compute_r_exp_cons_scaled(s0, ds0, b0, db0, lumi_factors):
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
        r_exp_cons = (s - 1.64 * ds) / s95exp

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


# === Example usage of compute_r_exp_cons_scaled ===
if __name__ == "__main__":
    baseline = {
        "s0": 5.2865,
        "ds0": 0.3766,
        "b0": 2.8,
        "db0": 0.9
    }

    lumi_factors = [1,  10]

    results = compute_r_exp_cons_scaled(**baseline, lumi_factors=lumi_factors)

    print("\n===== Luminosity Scaling Study =====")
    for res in results:
        print(f"Luminosity x{res['luminosity_factor']:>2}: "
              f"s95exp = {res['s95exp']:.4f}, "
              f"r_exp_cons = {res['r_exp_cons']:.5f}")
    print("====================================\n")

    baseline = {
        "s0": 2.3,
        "ds0": 0.0,
        "b0": 0.0001,
        "db0": 0.0
    }

    lumi_factors = [1,  10]

    results = compute_r_exp_cons_scaled(**baseline, lumi_factors=lumi_factors)

    print("\n===== Luminosity Scaling Study =====")
    for res in results:
        print(f"Luminosity x{res['luminosity_factor']:>2}: "
              f"s95exp = {res['s95exp']:.4f}, "
              f"r_exp_cons = {res['r_exp_cons']:.5f}")
    print("====================================\n")
