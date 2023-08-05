import numpy as np

from statsmodels.tools.tools import Bunch

llf = np.array([-239.75290561974])

nobs = np.array([202])

k = np.array([4])

k_exog = np.array([1])

sigma = np.array([.79291203639424])

chi2 = np.array([35036.682546665])

df_model = np.array([3])

k_ar = np.array([1])

k_ma = np.array([2])

params = np.array([
    .99954097483478,
    -.69022779461512,
    -.20477682541104,
    .62870949745886])

cov_params = np.array([
    .00007344276568,
    -.00016074342677,
    -.00018478942445,
    8.040251506e-06,
    -.00016074342677,
    .00094099304774,
    .00017233777676,
    -.0000145011098,
    -.00018478942445,
    .00017233777676,
    .00103352686916,
    .00030686101903,
    8.040251506e-06,
    -.0000145011098,
    .00030686101903,
    .00067796985496]).reshape(4, 4)

xb = np.array([
    0,
    0,
    .05104803293943,
    .06663129478693,
    .02164618112147,
    .0773858949542,
    .02606418170035,
    .09391833096743,
    .05710592120886,
    .03083370067179,
    .07319989800453,
    .05287836492062,
    .05776296555996,
    .09105986356735,
    .04293738678098,
    .09576436132193,
    .06068528071046,
    .06157376244664,
    .11172580718994,
    .06527806818485,
    .11443704366684,
    .05653077363968,
    .08205550909042,
    .08481238037348,
    .10436166077852,
    .0875685736537,
    .12320486456156,
    .08366665989161,
    .13979130983353,
    .1902572363615,
    .1306214183569,
    .21803694963455,
    .11079790443182,
    .17274764180183,
    .1937662512064,
    .20047917962074,
    .24034893512726,
    .21783453226089,
    .29279819130898,
    .26804205775261,
    .28678458929062,
    .35651323199272,
    .33659368753433,
    .35760068893433,
    .39895334839821,
    .41131839156151,
    .36645981669426,
    .40991494059563,
    .41024547815323,
    .32657703757286,
    .42312324047089,
    .34933325648308,
    .35912537574768,
    .35077446699142,
    .34701564908028,
    .37364318966866,
    .40170526504517,
    .56070649623871,
    .41915491223335,
    .73478156328201,
    .67748892307281,
    .7744625210762,
    .77825599908829,
    .97586625814438,
    .88692498207092,
    .76232481002808,
    .87376874685287,
    .83281141519547,
    .84783887863159,
    .66423743963242,
    .84904235601425,
    .81613594293594,
    .80033475160599,
    .95782464742661,
    .80624777078629,
    .83626395463943,
    .91873735189438,
    .95130664110184,
    1.0939226150513,
    1.1171194314957,
    1.1004731655121,
    1.3512066602707,
    1.4703129529953,
    1.4805699586868,
    1.7385860681534,
    1.8268398046494,
    1.5489361286163,
    1.7446503639221,
    1.864644408226,
    1.7200467586517,
    1.9223358631134,
    1.775306224823,
    1.5392524003983,
    1.4067870378494,
    1.9366238117218,
    1.2984343767166,
    1.1080636978149,
    1.3500427007675,
    1.2837564945221,
    1.2670782804489,
    1.3347851037979,
    1.2857422828674,
    1.1625040769577,
    1.2111755609512,
    1.0548515319824,
    1.2553508281708,
    1.0327949523926,
    1.0740388631821,
    1.222040772438,
    .40555971860886,
    1.0233588218689,
    .84209614992142,
    1.0186324119568,
    1.0319027900696,
    .99487775564194,
    1.0439211130142,
    .98785293102264,
    1.0620124340057,
    1.0916963815689,
    1.1378232240677,
    1.1243290901184,
    1.3305295705795,
    1.1925677061081,
    1.0872994661331,
    1.4599523544312,
    1.2333589792252,
    1.3584797382355,
    1.7595859766006,
    1.3009568452835,
    1.1157965660095,
    1.2948887348175,
    1.2063180208206,
    1.2332669496536,
    1.2132470607758,
    1.2049551010132,
    1.2260574102402,
    1.1875206232071,
    1.1547852754593,
    1.0519831180573,
    1.1594845056534,
    1.0069926977158,
    1.0675266981125,
    1.1299223899841,
    1.0620901584625,
    1.0999356508255,
    1.1535499095917,
    1.0026944875717,
    1.0428657531738,
    1.1120204925537,
    1.1684119701385,
    1.0258769989014,
    1.1342295408249,
    1.1183958053589,
    .91313683986664,
    .91156214475632,
    1.0540328025818,
    .84359037876129,
    .75758427381516,
    .96401190757751,
    .83226495981216,
    .8759680390358,
    .98239886760712,
    .85917687416077,
    1.0634194612503,
    .99442666769028,
    1.153311252594,
    1.2288066148758,
    1.0869039297104,
    1.281947016716,
    1.0067318677902,
    1.1028815507889,
    .82448446750641,
    .78489726781845,
    1.1850204467773,
    .86753690242767,
    1.0692945718765,
    1.1030179262161,
    .8791960477829,
    .86451041698456,
    1.0455346107483,
    1.085998415947,
    1.0172398090363,
    1.2250980138779,
    1.2316122055054,
    1.062157869339,
    1.3991860151291,
    1.0520887374878,
    2.2203133106232,
    .88833123445511,
    1.4289729595184,
    1.5206423997879,
    .68520504236221,
    1.4659557342529,
    1.5350053310394,
    1.3178979158401,
    1.4888265132904,
    1.9698411226273,
    1.4406447410583,
    2.517040014267,
    .55537897348404,
    -.20722626149654,
    1.0899519920349,
    1.164245724678])

y = np.array([
    np.nan,
    28.979999542236,
    29.201047897339,
    29.416631698608,
    29.391647338867,
    29.617385864258,
    29.576063156128,
    29.84391784668,
    29.897106170654,
    29.84083366394,
    29.993200302124,
    30.032876968384,
    30.097763061523,
    30.3010597229,
    30.262937545776,
    30.475763320923,
    30.500686645508,
    30.541572570801,
    30.801725387573,
    30.815279006958,
    31.054437637329,
    31.006530761719,
    31.102056503296,
    31.20481300354,
    31.384363174438,
    31.467567443848,
    31.703205108643,
    31.733665466309,
    32.019790649414,
    32.47025680542,
    32.580623626709,
    33.068035125732,
    33.010799407959,
    33.272747039795,
    33.593769073486,
    33.900478363037,
    34.340347290039,
    34.617835998535,
    35.192798614502,
    35.568042755127,
    35.986785888672,
    36.656513214111,
    37.13659286499,
    37.657600402832,
    38.29895401001,
    38.911319732666,
    39.266460418701,
    39.809917449951,
    40.310245513916,
    40.426574707031,
    41.023120880127,
    41.249336242676,
    41.559127807617,
    41.850772857666,
    42.14701461792,
    42.573642730713,
    43.101707458496,
    44.260707855225,
    44.619155883789,
    46.334781646729,
    47.477489471436,
    48.874462127686,
    50.078254699707,
    51.9758644104,
    53.186923980713,
    53.762325286865,
    54.873767852783,
    55.732814788818,
    56.647838592529,
    56.764236450195,
    57.849040985107,
    58.716136932373,
    59.500335693359,
    60.957824707031,
    61.606246948242,
    62.436264038086,
    63.61873626709,
    64.85131072998,
    66.593925476074,
    68.21711730957,
    69.600471496582,
    71.951202392578,
    74.470314025879,
    76.680564880371,
    79.738586425781,
    82.726844787598,
    84.148933410645,
    86.444648742676,
    89.064643859863,
    90.820045471191,
    93.422332763672,
    95.175308227539,
    95.939254760742,
    96.406784057617,
    99.436622619629,
    99.398429870605,
    99.00806427002,
    100.15004730225,
    101.08376312256,
    102.06707763672,
    103.43478393555,
    104.58574676514,
    105.26250457764,
    106.31117248535,
    106.75485229492,
    108.25534820557,
    108.73279571533,
    109.57403564453,
    111.12203979492,
    109.10556030273,
    110.52336120605,
    111.04209136963,
    112.41863250732,
    113.73190307617,
    114.79488372803,
    116.04392242432,
    116.98785400391,
    118.26200866699,
    119.59169769287,
    121.03782653809,
    122.32432556152,
    124.4305267334,
    125.69256591797,
    126.4873046875,
    128.95994567871,
    130.13334655762,
    131.85847473145,
    135.15957641602,
    136.00096130371,
    136.21580505371,
    137.49488830566,
    138.40631103516,
    139.53326416016,
    140.61323547363,
    141.70495605469,
    142.9260559082,
    143.98751831055,
    144.95478820801,
    145.55198669434,
    146.7594909668,
    147.30699157715,
    148.26751708984,
    149.52992248535,
    150.46208190918,
    151.59992980957,
    152.95355224609,
    153.60270690918,
    154.54286193848,
    155.81201171875,
    157.2684173584,
    158.02587890625,
    159.33422851563,
    160.51838684082,
    160.81312561035,
    161.31155395508,
    162.55403137207,
    162.84359741211,
    162.95758056641,
    164.16400146484,
    164.73225402832,
    165.57595825195,
    166.88238525391,
    167.55917358398,
    169.16342163086,
    170.29443359375,
    172.0532989502,
    173.92880249023,
    174.9868927002,
    176.88195800781,
    177.40672302246,
    178.50286865234,
    178.42448425293,
    178.48489379883,
    180.48501586914,
    180.86753845215,
    182.26928710938,
    183.70301818848,
    184.07919311523,
    184.56451416016,
    185.94552612305,
    187.38600158691,
    188.41723632813,
    190.32510375977,
    192.03161621094,
    192.8621673584,
    195.19918823242,
    195.7520904541,
    201.42030334473,
    200.28833007813,
    202.12896728516,
    204.22064208984,
    202.58520507813,
    205.03996276855,
    207.45500183105,
    208.65589904785,
    210.62182617188,
    214.46484375,
    215.4376373291,
    221.12704467773,
    217.44438171387,
    211.96676635742,
    213.76095581055,
    215.63323974609])

resid = np.array([
    np.nan,
    .17000007629395,
    .14895272254944,
    -.04663083329797,
    .14835388958454,
    -.067387573421,
    .17393657565117,
    -.00391817837954,
    -.08710660785437,
    .07916691154242,
    -.01320043392479,
    .00712300790474,
    .11223520338535,
    -.08105963468552,
    .11706246435642,
    -.03576298803091,
    -.0206862706691,
    .14842723309994,
    -.05172633752227,
    .12472246587276,
    -.104436814785,
    .01346892025322,
    .01794487424195,
    .07518746703863,
    -.00436318712309,
    .11243218928576,
    -.05320516973734,
    .14633287489414,
    .26020830869675,
    -.02025525644422,
    .26937630772591,
    -.16803389787674,
    .08919904381037,
    .12725540995598,
    .10623299330473,
    .1995185315609,
    .05965411290526,
    .28216546773911,
    .10719951242208,
    .13195945322514,
    .31321388483047,
    .14348678290844,
    .16340629756451,
    .24240159988403,
    .20104511082172,
    -.01131687406451,
    .13354018330574,
    .09008505195379,
    -.21024852991104,
    .1734229773283,
    -.12312019616365,
    -.04933403432369,
    -.05912613496184,
    -.05077522993088,
    .05298588424921,
    .12635681033134,
    .59829473495483,
    -.06070650368929,
    .98084276914597,
    .46521919965744,
    .62251031398773,
    .42553821206093,
    .92174476385117,
    .32413294911385,
    -.18692423403263,
    .23767517507076,
    .02623280882835,
    .06718628853559,
    -.54783964157104,
    .23576405644417,
    .05095916613936,
    -.01613672077656,
    .49966445565224,
    -.1578253954649,
    -.00624855514616,
    .26373836398125,
    .28126338124275,
    .64869183301926,
    .50607579946518,
    .28288212418556,
    .99952530860901,
    1.0487948656082,
    .72968405485153,
    1.319433093071,
    1.1614154577255,
    -.126842841506,
    .55106240510941,
    .75534957647324,
    .03535716608167,
    .67995470762253,
    -.02233435213566,
    -.775306224823,
    -.93925392627716,
    1.0932129621506,
    -1.3366253376007,
    -1.4984313249588,
    -.20806217193604,
    -.35004270076752,
    -.28375649452209,
    .03291719779372,
    -.13478049635887,
    -.48574689030647,
    -.16250413656235,
    -.61117708683014,
    .24515150487423,
    -.55535387992859,
    -.23279193043709,
    .32596263289452,
    -2.4220454692841,
    .39444333314896,
    -.32336190342903,
    .3579084277153,
    .28136301040649,
    .06810333579779,
    .20511920750141,
    -.04392115399241,
    .2121440321207,
    .23799060285091,
    .30830511450768,
    .16217225790024,
    .77567237615585,
    .06947190314531,
    -.29256621003151,
    1.012699007988,
    -.05995841696858,
    .36664715409279,
    1.5415141582489,
    -.45958289504051,
    -.90094763040543,
    -.01580573618412,
    -.29488867521286,
    -.10631188750267,
    -.13327611982822,
    -.11324090510607,
    -.00495810527354,
    -.12605135142803,
    -.18752062320709,
    -.45478835701942,
    .04802301898599,
    -.45948752760887,
    -.1069987937808,
    .13247023522854,
    -.12992236018181,
    .0379159450531,
    .20006743073463,
    -.35354685783386,
    -.10270062834024,
    .15713113546371,
    .28798860311508,
    -.26841807365417,
    .17411996424198,
    .06576746702194,
    -.61839586496353,
    -.41313683986664,
    .18844394385815,
    -.55403280258179,
    -.6435934305191,
    .24241572618484,
    -.26401495933533,
    -.03226193040609,
    .32402887940407,
    -.1823958158493,
    .54083228111267,
    .13657745718956,
    .60556417703629,
    .64669179916382,
    -.02880969829857,
    .61310833692551,
    -.48195922374725,
    -.00673185009509,
    -.90286934375763,
    -.72449362277985,
    .81510883569717,
    -.48502343893051,
    .33246004581451,
    .33071464300156,
    -.50302714109421,
    -.3791960477829,
    .33548650145531,
    .35447460412979,
    .01399240642786,
    .682772397995,
    .474898904562,
    -.23161220550537,
    .93784213066101,
    -.49919214844704,
    3.4479112625122,
    -2.020316362381,
    .41167178750038,
    .57102704048157,
    -2.3206453323364,
    .98880618810654,
    .8800373673439,
    -.11700607091188,
    .47710022330284,
    1.8731729984283,
    -.46784225106239,
    3.1723618507385,
    -4.2380332946777,
    -5.2703905105591,
    .70423555374146,
    .70803683996201,
    .7517546415329])

yr = np.array([
    np.nan,
    .17000007629395,
    .14895272254944,
    -.04663083329797,
    .14835388958454,
    -.067387573421,
    .17393657565117,
    -.00391817837954,
    -.08710660785437,
    .07916691154242,
    -.01320043392479,
    .00712300790474,
    .11223520338535,
    -.08105963468552,
    .11706246435642,
    -.03576298803091,
    -.0206862706691,
    .14842723309994,
    -.05172633752227,
    .12472246587276,
    -.104436814785,
    .01346892025322,
    .01794487424195,
    .07518746703863,
    -.00436318712309,
    .11243218928576,
    -.05320516973734,
    .14633287489414,
    .26020830869675,
    -.02025525644422,
    .26937630772591,
    -.16803389787674,
    .08919904381037,
    .12725540995598,
    .10623299330473,
    .1995185315609,
    .05965411290526,
    .28216546773911,
    .10719951242208,
    .13195945322514,
    .31321388483047,
    .14348678290844,
    .16340629756451,
    .24240159988403,
    .20104511082172,
    -.01131687406451,
    .13354018330574,
    .09008505195379,
    -.21024852991104,
    .1734229773283,
    -.12312019616365,
    -.04933403432369,
    -.05912613496184,
    -.05077522993088,
    .05298588424921,
    .12635681033134,
    .59829473495483,
    -.06070650368929,
    .98084276914597,
    .46521919965744,
    .62251031398773,
    .42553821206093,
    .92174476385117,
    .32413294911385,
    -.18692423403263,
    .23767517507076,
    .02623280882835,
    .06718628853559,
    -.54783964157104,
    .23576405644417,
    .05095916613936,
    -.01613672077656,
    .49966445565224,
    -.1578253954649,
    -.00624855514616,
    .26373836398125,
    .28126338124275,
    .64869183301926,
    .50607579946518,
    .28288212418556,
    .99952530860901,
    1.0487948656082,
    .72968405485153,
    1.319433093071,
    1.1614154577255,
    -.126842841506,
    .55106240510941,
    .75534957647324,
    .03535716608167,
    .67995470762253,
    -.02233435213566,
    -.775306224823,
    -.93925392627716,
    1.0932129621506,
    -1.3366253376007,
    -1.4984313249588,
    -.20806217193604,
    -.35004270076752,
    -.28375649452209,
    .03291719779372,
    -.13478049635887,
    -.48574689030647,
    -.16250413656235,
    -.61117708683014,
    .24515150487423,
    -.55535387992859,
    -.23279193043709,
    .32596263289452,
    -2.4220454692841,
    .39444333314896,
    -.32336190342903,
    .3579084277153,
    .28136301040649,
    .06810333579779,
    .20511920750141,
    -.04392115399241,
    .2121440321207,
    .23799060285091,
    .30830511450768,
    .16217225790024,
    .77567237615585,
    .06947190314531,
    -.29256621003151,
    1.012699007988,
    -.05995841696858,
    .36664715409279,
    1.5415141582489,
    -.45958289504051,
    -.90094763040543,
    -.01580573618412,
    -.29488867521286,
    -.10631188750267,
    -.13327611982822,
    -.11324090510607,
    -.00495810527354,
    -.12605135142803,
    -.18752062320709,
    -.45478835701942,
    .04802301898599,
    -.45948752760887,
    -.1069987937808,
    .13247023522854,
    -.12992236018181,
    .0379159450531,
    .20006743073463,
    -.35354685783386,
    -.10270062834024,
    .15713113546371,
    .28798860311508,
    -.26841807365417,
    .17411996424198,
    .06576746702194,
    -.61839586496353,
    -.41313683986664,
    .18844394385815,
    -.55403280258179,
    -.6435934305191,
    .24241572618484,
    -.26401495933533,
    -.03226193040609,
    .32402887940407,
    -.1823958158493,
    .54083228111267,
    .13657745718956,
    .60556417703629,
    .64669179916382,
    -.02880969829857,
    .61310833692551,
    -.48195922374725,
    -.00673185009509,
    -.90286934375763,
    -.72449362277985,
    .81510883569717,
    -.48502343893051,
    .33246004581451,
    .33071464300156,
    -.50302714109421,
    -.3791960477829,
    .33548650145531,
    .35447460412979,
    .01399240642786,
    .682772397995,
    .474898904562,
    -.23161220550537,
    .93784213066101,
    -.49919214844704,
    3.4479112625122,
    -2.020316362381,
    .41167178750038,
    .57102704048157,
    -2.3206453323364,
    .98880618810654,
    .8800373673439,
    -.11700607091188,
    .47710022330284,
    1.8731729984283,
    -.46784225106239,
    3.1723618507385,
    -4.2380332946777,
    -5.2703905105591,
    .70423555374146,
    .70803683996201,
    .7517546415329])

mse = np.array([
    .95459979772568,
    .71522510051727,
    .63122135400772,
    .6314896941185,
    .63029319047928,
    .63014930486679,
    .62988424301147,
    .62969470024109,
    .62953060865402,
    .6293950676918,
    .62928181886673,
    .62918740510941,
    .62910866737366,
    .62904292345047,
    .62898802757263,
    .6289421916008,
    .62890386581421,
    .62887191772461,
    .62884521484375,
    .6288229227066,
    .62880426645279,
    .6287887096405,
    .6287756562233,
    .62876480817795,
    .62875574827194,
    .62874811887741,
    .62874180078506,
    .62873649597168,
    .62873202562332,
    .62872833013535,
    .62872523069382,
    .62872266769409,
    .62872052192688,
    .62871867418289,
    .62871718406677,
    .62871593236923,
    .62871485948563,
    .62871396541595,
    .62871325016022,
    .62871265411377,
    .62871211767197,
    .62871170043945,
    .62871134281158,
    .62871104478836,
    .62871074676514,
    .6287105679512,
    .62871038913727,
    .62871026992798,
    .62871015071869,
    .6287100315094,
    .62870991230011,
    .62870985269547,
    .62870979309082,
    .62870973348618,
    .62870973348618,
    .62870967388153,
    .62870967388153,
    .62870961427689,
    .62870961427689,
    .62870955467224,
    .62870955467224,
    .62870955467224,
    .62870955467224,
    .62870955467224,
    .62870955467224,
    .62870955467224,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676,
    .6287094950676])

stdp = np.array([
    0,
    0,
    .05104803293943,
    .06663129478693,
    .02164618112147,
    .0773858949542,
    .02606418170035,
    .09391833096743,
    .05710592120886,
    .03083370067179,
    .07319989800453,
    .05287836492062,
    .05776296555996,
    .09105986356735,
    .04293738678098,
    .09576436132193,
    .06068528071046,
    .06157376244664,
    .11172580718994,
    .06527806818485,
    .11443704366684,
    .05653077363968,
    .08205550909042,
    .08481238037348,
    .10436166077852,
    .0875685736537,
    .12320486456156,
    .08366665989161,
    .13979130983353,
    .1902572363615,
    .1306214183569,
    .21803694963455,
    .11079790443182,
    .17274764180183,
    .1937662512064,
    .20047917962074,
    .24034893512726,
    .21783453226089,
    .29279819130898,
    .26804205775261,
    .28678458929062,
    .35651323199272,
    .33659368753433,
    .35760068893433,
    .39895334839821,
    .41131839156151,
    .36645981669426,
    .40991494059563,
    .41024547815323,
    .32657703757286,
    .42312324047089,
    .34933325648308,
    .35912537574768,
    .35077446699142,
    .34701564908028,
    .37364318966866,
    .40170526504517,
    .56070649623871,
    .41915491223335,
    .73478156328201,
    .67748892307281,
    .7744625210762,
    .77825599908829,
    .97586625814438,
    .88692498207092,
    .76232481002808,
    .87376874685287,
    .83281141519547,
    .84783887863159,
    .66423743963242,
    .84904235601425,
    .81613594293594,
    .80033475160599,
    .95782464742661,
    .80624777078629,
    .83626395463943,
    .91873735189438,
    .95130664110184,
    1.0939226150513,
    1.1171194314957,
    1.1004731655121,
    1.3512066602707,
    1.4703129529953,
    1.4805699586868,
    1.7385860681534,
    1.8268398046494,
    1.5489361286163,
    1.7446503639221,
    1.864644408226,
    1.7200467586517,
    1.9223358631134,
    1.775306224823,
    1.5392524003983,
    1.4067870378494,
    1.9366238117218,
    1.2984343767166,
    1.1080636978149,
    1.3500427007675,
    1.2837564945221,
    1.2670782804489,
    1.3347851037979,
    1.2857422828674,
    1.1625040769577,
    1.2111755609512,
    1.0548515319824,
    1.2553508281708,
    1.0327949523926,
    1.0740388631821,
    1.222040772438,
    .40555971860886,
    1.0233588218689,
    .84209614992142,
    1.0186324119568,
    1.0319027900696,
    .99487775564194,
    1.0439211130142,
    .98785293102264,
    1.0620124340057,
    1.0916963815689,
    1.1378232240677,
    1.1243290901184,
    1.3305295705795,
    1.1925677061081,
    1.0872994661331,
    1.4599523544312,
    1.2333589792252,
    1.3584797382355,
    1.7595859766006,
    1.3009568452835,
    1.1157965660095,
    1.2948887348175,
    1.2063180208206,
    1.2332669496536,
    1.2132470607758,
    1.2049551010132,
    1.2260574102402,
    1.1875206232071,
    1.1547852754593,
    1.0519831180573,
    1.1594845056534,
    1.0069926977158,
    1.0675266981125,
    1.1299223899841,
    1.0620901584625,
    1.0999356508255,
    1.1535499095917,
    1.0026944875717,
    1.0428657531738,
    1.1120204925537,
    1.1684119701385,
    1.0258769989014,
    1.1342295408249,
    1.1183958053589,
    .91313683986664,
    .91156214475632,
    1.0540328025818,
    .84359037876129,
    .75758427381516,
    .96401190757751,
    .83226495981216,
    .8759680390358,
    .98239886760712,
    .85917687416077,
    1.0634194612503,
    .99442666769028,
    1.153311252594,
    1.2288066148758,
    1.0869039297104,
    1.281947016716,
    1.0067318677902,
    1.1028815507889,
    .82448446750641,
    .78489726781845,
    1.1850204467773,
    .86753690242767,
    1.0692945718765,
    1.1030179262161,
    .8791960477829,
    .86451041698456,
    1.0455346107483,
    1.085998415947,
    1.0172398090363,
    1.2250980138779,
    1.2316122055054,
    1.062157869339,
    1.3991860151291,
    1.0520887374878,
    2.2203133106232,
    .88833123445511,
    1.4289729595184,
    1.5206423997879,
    .68520504236221,
    1.4659557342529,
    1.5350053310394,
    1.3178979158401,
    1.4888265132904,
    1.9698411226273,
    1.4406447410583,
    2.517040014267,
    .55537897348404,
    -.20722626149654,
    1.0899519920349,
    1.164245724678])

icstats = np.array([
    202,
    np.nan,
    -239.75290561974,
    4,
    487.50581123949,
    500.73888202909])


results = Bunch(
    llf=llf,
    nobs=nobs,
    k=k,
    k_exog=k_exog,
    sigma=sigma,
    chi2=chi2,
    df_model=df_model,
    k_ar=k_ar,
    k_ma=k_ma,
    params=params,
    cov_params=cov_params,
    xb=xb,
    y=y,
    resid=resid,
    yr=yr,
    mse=mse,
    stdp=stdp,
    icstats=icstats
)
