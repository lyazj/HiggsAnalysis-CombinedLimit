#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser(description="Plot expected and observed 1D scan results.")
parser.add_argument("--exp", help="Path to the expected scan results file")
parser.add_argument("--obs", help="Path to the observed scan results file")
parser.add_argument("--out", required=True, help="Output file name for the plot")
parser.add_argument("--poi", required=True, help="Parameter of interest")
parser.add_argument("--label", default="Preliminary", help="Label for the plot")
parser.add_argument("--xlabel", default=None, help="X-axis label")
parser.add_argument("--year", default=None, help="Data-taking year(s)")
parser.add_argument("--lumi", default="200", help="Integrated luminosity (fb^-1)")
parser.add_argument("--com", default="13 and 13.6", help="Center-of-mass energy")
args = parser.parse_args()

import uproot
import matplotlib.pyplot as plt
import mplhep as hep
from scipy.interpolate import UnivariateSpline
import numpy as np


def find_crossings_with_spline(x, y, x_best, target):
    spline = UnivariateSpline(x, y - target, s=0)
    roots = spline.roots()
    r_l = roots[roots <= x_best]
    r_r = roots[roots >= x_best]
    if len(r_l) == 0:
        r_l = np.array([-np.inf])
    if len(r_r) == 0:
        r_r = np.array([np.inf])
    return r_l[-1], r_r[0]


hep.style.use("CMS")
hep.cms.label(data=True, label=args.label or None, year=args.year or None, lumi=args.lumi or None, com=args.com or None)
if args.exp:
    exp = uproot.open(args.exp)["limit"].arrays([args.poi, "deltaNLL"])
    x_exp = exp[args.poi]
    y_exp = 2 * exp["deltaNLL"]
    xl_exp, xr_exp = find_crossings_with_spline(x_exp[1:], y_exp[1:], x_exp[0], 1.0)
    plt.plot(x_exp[:1], y_exp[:1], "o", color="black")
    plt.plot(
        x_exp[1:],
        y_exp[1:],
        ".--",
        label=f"Expected (${x_exp[0]:.3f}^{{+{xr_exp - x_exp[0]:.3f}}}_{{-{x_exp[0] - xl_exp:.3f}}}$)",
        color="black",
    )
if args.obs:
    obs = uproot.open(args.obs)["limit"].arrays([args.poi, "deltaNLL"])
    x_obs = obs[args.poi]
    y_obs = 2 * obs["deltaNLL"]
    xl_obs, xr_obs = find_crossings_with_spline(x_obs[1:], y_obs[1:], x_obs[0], 1.0)
    plt.plot(x_obs[:1], y_obs[:1], "o", color="black")
    plt.plot(
        x_obs[1:],
        y_obs[1:],
        "*-",
        label=f"Observed (${x_obs[0]:.3f}^{{+{xr_obs - x_obs[0]:.3f}}}_{{-{x_obs[0] - xl_obs:.3f}}}$)",
        color="black",
    )
plt.axhline(1.0, color="gray")
plt.axhline(4.0, color="gray")
plt.xlabel(args.xlabel or args.poi, loc="center")
plt.ylabel(r"$-2\Delta\log L$", loc="center")
plt.grid()
plt.legend()
plt.tight_layout()
plt.savefig(args.out)
