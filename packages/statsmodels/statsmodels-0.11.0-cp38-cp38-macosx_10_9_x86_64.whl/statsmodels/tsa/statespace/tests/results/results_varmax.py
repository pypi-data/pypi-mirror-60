"""
Results for VARMAX tests

Results from Stata using script `test_varmax_stata.do`.
See also Stata time series documentation, in particular `dfactor`.

Data from:

http://www.jmulti.de/download/datasets/e1.dat

Author: Chad Fulton
License: Simplified-BSD
"""

# See http://www.jmulti.de/download/datasets/e1.dat
# 1960:Q1 - 1982Q4
lutkepohl_data = [
    [180, 451, 415], [179, 465, 421], [185, 485, 434], [192, 493, 448],
    [211, 509, 459], [202, 520, 458], [207, 521, 479], [214, 540, 487],
    [231, 548, 497], [229, 558, 510], [234, 574, 516], [237, 583, 525],
    [206, 591, 529], [250, 599, 538], [259, 610, 546], [263, 627, 555],
    [264, 642, 574], [280, 653, 574], [282, 660, 586], [292, 694, 602],
    [286, 709, 617], [302, 734, 639], [304, 751, 653], [307, 763, 668],
    [317, 766, 679], [314, 779, 686], [306, 808, 697], [304, 785, 688],
    [292, 794, 704], [275, 799, 699], [273, 799, 709], [301, 812, 715],
    [280, 837, 724], [289, 853, 746], [303, 876, 758], [322, 897, 779],
    [315, 922, 798], [339, 949, 816], [364, 979, 837], [371, 988, 858],
    [375, 1025, 881], [432, 1063, 905], [453, 1104, 934], [460, 1131, 968],
    [475, 1137, 983], [496, 1178, 1013], [494, 1211, 1034], [498, 1256, 1064],
    [526, 1290, 1101], [519, 1314, 1102], [516, 1346, 1145], [531, 1385, 1173],
    [573, 1416, 1216], [551, 1436, 1229], [538, 1462, 1242], [532, 1493, 1267],
    [558, 1516, 1295], [524, 1557, 1317], [525, 1613, 1355], [519, 1642, 1371],
    [526, 1690, 1402], [510, 1759, 1452], [519, 1756, 1485], [538, 1780, 1516],
    [549, 1807, 1549], [570, 1831, 1567], [559, 1873, 1588], [584, 1897, 1631],
    [611, 1910, 1650], [597, 1943, 1685], [603, 1976, 1722], [619, 2018, 1752],
    [635, 2040, 1774], [658, 2070, 1807], [675, 2121, 1831], [700, 2132, 1842],
    [692, 2199, 1890], [759, 2253, 1958], [782, 2276, 1948], [816, 2318, 1994],
    [844, 2369, 2061], [830, 2423, 2056], [853, 2457, 2102], [852, 2470, 2121],
    [833, 2521, 2145], [860, 2545, 2164], [870, 2580, 2206], [830, 2620, 2225],
    [801, 2639, 2235], [824, 2618, 2237], [831, 2628, 2250], [830, 2651, 2271],
]

lutkepohl_var1 = {
    'params': [
        -0.25034303,  0.28759168,  0.81626475,  # Phi, row 1
        0.023383,     0.19048278,  0.66502259,  # Phi, row 2
        -0.01492992,  0.53796097,  0.28114733,  # Phi, row 3
        # .00199294,                              # Covariance, lower triangle
        # .00006096, .00012986,
        # .00018523, .00011695, .00016188,
        # Note: the following are the Cholesky of the covariance
        # matrix defined just above
        0.04464236,                             # Cholesky, lower triangle
        0.00136552,  0.01354125,
        0.0029089,   0.00834324,  0.00915471
    ],
    'var_oim': [
        .01319669, .19413864, .2386643,
        .0012437,  .01829378, .02234399,
        .00107749, .01584584, .01938099,
        1.061e-07,
        4.981e-09, 4.549e-09,
        9.211e-10, 5.825e-10, 7.016e-10],
    'loglike': 587.8481018831948,
    'aic': -1145.696,
    'bic': -1110.934,
}

lutkepohl_var1_diag = {
    'params': [
        -0.24817904,  0.29283012,  0.80794938,  # Phi, row 1
        0.02282985,   0.19672157,  0.66329776,  # Phi, row 2
        -0.01522531,  0.53500874,  0.28859213,  # Phi, row 3
        0.00199106,  0.00018529,  0.00016179    # Variances, diagonal
    ],
    'var_oim': [
        .01314245, .1902972,  .23400828,
        .00124336, .01840132, .02229946,
        .00107322, .01558391, .01909303,
        1.057e-07, 9.233e-10, 7.011e-10
    ],
    'loglike': 562.8168476509002,
    'aic': -1101.634,
    'bic': -1073.824
}

lutkepohl_var1_diag_meas = {
    'params': [
        -0.24817904,  0.29283012,  0.80794938,  # Phi, row 1
        0.02282985,   0.19672157,  0.66329776,  # Phi, row 2
        -0.01522531,  0.53500874,  0.28859213,  # Phi, row 3
        0.00199106,   0.00018529,  0.00016179,  # Variances, diagonal
        0,            0,           0            # Measurement error variances
    ],
    'var_oim': [
        .01314245, .1902972,  .23400828,
        .00124336, .01840132, .02229946,
        .00107322, .01558391, .01909303,
        1.057e-07, 9.233e-10, 7.011e-10,
        None, None, None
    ],
    'loglike': 562.8168476509002,
    'aic': None,
    'bic': None
}

lutkepohl_var1_obs_intercept = {
    'params': [
        -.24762,   .25961003,  .75992623,   # Phi, row 1
        .03186854, -.07271862, .23697765,   # Phi, row 2
        -.0053055, .2362571,   -.19438311,  # Phi, row 3
        .00199116, .00013515,  .00009937    # Variances, diagonal
    ],
    'obs_intercept': [.01799302, .02065458,  .01987525],  # Intercepts
    'var_oim': [
        .01317874, .2311403,  .33481866,
        .00090084, .0157839,  .0229119,
        .00065737, .01149729, .01661236,
        # .00001802, 1.818e-06, 1.086e-06,  # Intercept parameters
        1.057e-07, 4.869e-10, 2.630e-10],
    'loglike': 593.5252693885262,
    'aic': -1101.634,
    'bic': -1073.824
}

lutkepohl_var1_exog = {
    'params': [
        -.25549409, .31149462, .92674046,  # Phi, row 1
        .02935715,  .13699757, .5059042,   # Phi, row 2
        -.00540021, .4598014,  .06065565,  # Phi, row 3
        -.00007533, .00012771, .00018224,  # exog
        # .00200617,                         # Covariance, lower triangle
        # .00007053,  .00017216,
        # .00013934,  .00010021, .00013833
        # Note: the following are the Cholesky of the covariance
        # matrix defined just above
        .04479029,                         # Cholesky, lower triangle
        .00157467,  .01302614,
        .00311094,  .00731692, .00866687
    ],
    'var_oim': [
        .01350243, .20429977, .29684366,  # Phi, row 1
        .00115871, .01753203, .02547371,  # Phi, row 2
        .000931,   .01408662, .02046759,  # Phi, row 3
        3.720e-08, 3.192e-09, 2.565e-09   # exog
    ],
    'loglike': 587.4157014188437,
    'aic': None,
    'bic': None
}

lutkepohl_var1_exog2 = {
    'params': [
        -.2552236,  .21722691,  .81525457,  # Phi, row 1
        .02998355,  -.08130972, .24772266,  # Phi, row 2
        -.00476998, .24016112, -.19910237,  # Phi, row 3
        .00811096, -.00015244,  # exog, y1
        .01878355, -.00005086,  # exog, y2
        .01889825, 2.577e-06,   # exog, y3
        # .00199918,                         # Covariance, lower triangle
        # .00005435,  .00013469,
        # .00012306,  .00006251,   .00010039
        # Note: the following are the Cholesky of the covariance
        # matrix defined just above
        .04471219,                         # Cholesky, lower triangle
        .00121555,  .01102644,
        .00275227,  .00536569,  .00800152
    ],
    'var_oim': None,
    # 'loglike': 600.9801664685759,  # From Stata
    'loglike': 600.65449034396283,   # From VARMAX (regression test)
    'aic': None,
    'bic': None
}

lutkepohl_var2 = {
    'params': [
        -.25244981, .62528114,  # Phi_1, row 1
        -.13011679, .58173748,  # Phi_1, row 2
        .05369178,  .35716349,  # Phi_2, row 1
        .03861472,  .43812606,  # Phi_2, row 2
        # .00197786,              # Covariance, lower triangle
        # .00008091,  .00018269
        0.04447314,             # Covariance cholesky, lower triangle
        0.0018193, 0.01339329
    ],
    'var_oim': [
        .01315844, .11805816,  # Phi_1, row 1
        .01321036, .11300702,  # Phi_1, row 2
        .00122666, .01064478,  # Phi_2, row 1
        .0012571,  .0106738,   # Phi_2, row 2
        1.048e-07,             # Covariance, lower triangle
        4.994e-09, 8.940e-10
    ],
    'loglike': 343.3149718445623,
    'aic': -664.6299,
    'bic': -639.1376
}

fred_varma11 = {
    'params': [
        .80580312,  0,           # Phi_1, row 1
        .17348681,  -.48093755,  # Phi_1, row 2
        -.51890703, 0,           # Theta_1, row 1
        0,          0,           # Theta_1, row 2
        .0000582,   .00003815,   # Variances
    ],
    'var_oim': [
        .00272999,  0,          # Phi_1, row 1
        .00164152, .00248576,   # Phi_1, row 2
        .0049259,  0,           # Theta_1, row 1
        0,         0,           # Theta_1, row 2
        1.529e-11, 6.572e-12,   # Variances
    ],
    'loglike': 3156.056423235071,
    'aic': -6300.113,
    'bic': -6275.551
}

fred_vma1 = {
    'params': [
        .24803941, 0,          # Theta_1, row 1
        0,         0,          # Theta_1, row 2
        .00006514, .00004621,  # Variances
    ],
    'var_oim': [
        .00154773, 0,           # Theta_1, row 1
        0,         0,           # Theta_1, row 2
        1.916e-11, 9.639e-12,   # Variances
    ],
    'loglike': 3088.909619417645,
    'aic': -6171.819,
    'bic': -6159.539
}
