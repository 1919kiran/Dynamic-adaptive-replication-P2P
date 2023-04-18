import random

coordinates = [(6.607662345511912, -113.06342330255615), (-53.754444543459236, 68.6823710697071),
               (1.0873546312061535, -12.777061573491608), (0.6101409523467396, -92.39029773266704),
               (-72.26045169759311, -86.99979514829761), (24.314593554811353, 66.83964632586438),
               (28.326141458168593, -61.86735120201713), (-9.955077176463135, -138.3739479662181),
               (82.9510860532454, 171.75420245592107), (-8.571061604007326, 148.9206056458106),
               (-71.40252219135654, 48.875421943216935), (-30.514222813415962, 146.26228202747552),
               (57.06072136997281, 178.04738147214), (75.44388764180607, 165.5656602762549),
               (-41.252751948492, -47.05335879112147), (22.776250417933312, 141.54855883887996),
               (-4.593366606464713, 121.97508127412414), (70.92286875721899, -127.2482399320325),
               (-40.73274620661586, -132.39608416325854), (81.91672856909037, 155.72633036966266),
               (53.06865127694462, -113.12862473606408), (68.17814117330383, -45.141226129178335),
               (-76.37415051174621, 44.75407585201677), (-78.43861831174634, -22.86722816415545),
               (-20.74275745912138, 154.53777751478458), (4.90325483297741, -113.87517113786598),
               (69.16974092331688, -113.70545787721268), (-42.401414046599584, 23.770101692958548),
               (17.813331803791627, 22.53214028048535), (39.250760351919865, -42.792725763986226),
               (-85.4393913878229, -58.43045960039615), (-8.65090506868323, -79.03341338515105),
               (-71.30715855767642, 84.07588445699946), (-89.91749548763278, -106.18358087401407),
               (-31.840873746826908, 61.18417737174056), (63.45872550733111, -121.07050030092144),
               (75.47587563718756, 118.90864775978503), (-32.37758483268604, -134.91296971023195),
               (47.7679628290023, 174.38382894798866), (66.09897635128561, -78.98690398562462),
               (57.581694913154536, -11.636985974376984), (20.072894359526217, -78.103341113661),
               (81.65911785213669, 7.4702825376196245), (-0.698010321880929, -35.96895555253113),
               (-24.859764998865103, 78.9074293229753), (-60.95172113183902, 140.1691977912074),
               (85.76488094830069, 115.01968403169155), (-0.17247586014357807, -173.69423347627657),
               (-73.00783214505978, 32.66213243605094), (-64.78089009720043, -14.913997879551971),
               (32.71163464593326, -66.73284218871353), (-81.3466063416283, 79.80708543257089),
               (-81.53196994858587, -108.57681614952375), (-68.76652780541991, 81.48737925726033),
               (-28.663484865877038, 77.94236980290833), (79.25821386979143, 41.54703531247591),
               (41.105712214057945, 10.241332106796222), (-1.3059936219607096, 79.99433448931075),
               (-70.45038020906082, 106.28422050412155), (6.0221297373939535, -70.38482128812821),
               (26.80000116922463, 113.49055023268744), (56.40859615189564, 19.381772849531217),
               (22.939602976159037, -35.056560491537994), (-85.30026659405223, 160.46567075260776),
               (38.59313025537972, -111.27312814967011), (-49.809767633628674, -173.59485811189074),
               (73.1208213024151, -33.852654453388624), (26.20443222752708, -59.57057270856606),
               (-58.784719880702966, -27.223519750161785), (-16.36955021574093, -158.76315644133575),
               (24.200143356346445, 29.053995957625148), (-15.78325425188521, -107.4352591148584),
               (-37.500111846817376, 110.09811280505153), (-24.33247292973043, -158.44377069453373),
               (-75.78536716525873, -118.86811920672619), (14.899878304095878, -101.26141943576867),
               (-38.279749797091746, 27.515367921271576), (44.28337951144016, 35.21028443498682),
               (0.8969982149980922, 40.976082260047264), (-65.69255188754934, 122.24003826685231),
               (11.318460043093026, -67.03505021361258), (-21.791401541374697, 173.1768275396638),
               (3.32399387036331, -20.354029809327642), (-0.06740115586886475, 53.59669143182737),
               (-10.497283931435632, 162.14355678437215), (-10.3477488058263, -69.89834505118331),
               (-62.382239382740735, 145.5495606046133), (69.798749890592, 43.282424594061354),
               (-48.758646832629076, -143.36510343392268), (36.58814763988728, 70.58013915571792),
               (26.328973011735187, -169.31820147138015), (-84.84517716278906, -89.91932551964575),
               (-30.0737948901986, -79.09956784846678), (47.933572995571325, 132.707390992642),
               (-9.737914158247719, -151.41490985610972), (56.555445473353586, 21.91346858875218),
               (37.77245347064253, 130.70202119713986), (-42.164758012807326, 76.9141367340552),
               (-12.639909420556563, -60.27987609374952), (-21.185147119890814, 93.65505766612631)]


def get_location():
    return random.choice(coordinates)


def get_node_locations(num_nodes):
    return coordinates[0:num_nodes]
