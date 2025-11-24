import pyhf

# Use high-precision backend
pyhf.set_backend("numpy", precision="64b")

# Inputs from your CheckMATE best_signal_regions.txt
s = 5.2865     # signal yield
ds = 0.3766    # signal uncertainty
b = 2.8        # background yield
db = 0.9       # background uncertainty

# Define the model using normsys for both signal and background
model = pyhf.Model({
    "channels": [
        {
            "name": "sr",
            "samples": [
                {
                    "name": "signal",
                    "data": [s],
                    "modifiers": [
                        {"name": "mu", "type": "normfactor", "data": None},
                        {"name": "sig_unc", "type": "normsys", 
                         "data": {"hi": 1 + ds/s, "lo": 1 - ds/s}}
                    ]
                },
                {
                    "name": "background",
                    "data": [b],
                    "modifiers": [
                        {"name": "bkg_unc", "type": "normsys",
                         "data": {"hi": 1 + db/b, "lo": 1 - db/b}}
                    ]
                }
            ]
        }
    ]
})

# Asimov expected data: background only + nuisance params at nominal
params = [0.0, 0.0, 0.0]  # [mu=0, sig_unc=0, bkg_unc=0]
observed = model.expected_data(params).tolist()

# Compute upper limit on mu (signal strength)
mu_up = pyhf.infer.intervals.upper_limits.upper_limit(observed, model, level=0.05)
mu_up = mu_up[0]  # ✅ extract the scalar limit
s95 = mu_up * s
r = s / s95
print(f"s95exp (with ds) = {s95:.4f}")
print(f"r_pyhf (with ds) = {r:.5f}")
