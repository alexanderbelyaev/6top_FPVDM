import pyhf
import numpy as np

pyhf.set_backend("numpy", precision="64b")

# CheckMATE .txt input values
s = 5.2865
ds = 0.3766
b = 2.8
db = 0.9

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
