Copyright (c) 2020 Nico Piatkowski

pxpy
====
The python library for discrete pairwise undirected graphical models.

<https://randomfields.org>

Changelog
=========
* 1.0a21: Improved support for external inference engine (e.g., for MAP prediction)
* 1.0a20: Added support for external inference engine (e.g., hardware-assisted)
* 1.0a19: Fixed minor bugs in model creation
* 1.0a18: Added debug mode (linux only)
* 1.0a17: Simplified backend; added tests; fixed regularization bug; added AIC/BIC
* 1.0a16: Fixed memory leak; enabled training resumption; improved optimization hooks
* 1.0a15: Improved API
* 1.0a14: Improved memory management
* 1.0a13: Fixed memory leak with observed data
* 1.0a12: Simplified access to vertex and pairwise marginals
* 1.0a11: Added single variable marginals
* 1.0a10: Optimized library build
* 1.0a9:  Enabled sampling with observations; Fixed parameter name in marginal inference
* 1.0a8:  Fixed maximum a posteriori estimation; Added custom graph construction
* 1.0a7:  Multiple minor fixes; enabled marginal inference with observations; enabled minimal statistics
* 1.0a6:  Added manual model creation; enabled training data with missing values
* 1.0a5:  Fixed model management
* 1.0a4:  Added model access in regularization and proximal hooks
* 1.0a3:  Lower GLIBC requirement + removed libgomp dependency (linux)
* 1.0a2:  Python 3.5 compatibility
* 1.0a1:  Initial release
