import locuspeerexplorer.peer_finder as pe
import os
import sys
import pandas as pd
import unittest

sys.path.insert(0, "../locuspeerexplorer/")

dirname, filename = os.path.split(os.path.abspath(__file__))
# TEST_DIRECTORY = os.path.dirname(__file__)

sample = {
    "MSA": {
        635: 35620,
        636: 35660,
        637: 35840,
        638: 35980,
        639: 36100,
        640: 36140,
        641: 36220,
        642: 36260,
        643: 36420,
        644: 36500,
        645: 36540,
        646: 36740,
        647: 36780,
        648: 36980,
        649: 37100,
        650: 37340,
        651: 37460,
        652: 37620,
        653: 37860,
        654: 37900,
    },
    "MSA_NAME": {
        635: "New York-Newark-Jersey City, NY-NJ-PA",
        636: "Niles-Benton Harbor, MI",
        637: "North Port-Sarasota-Bradenton, FL",
        638: "Norwich-New London, CT",
        639: "Ocala, FL",
        640: "Ocean City, NJ",
        641: "Odessa, TX",
        642: "Ogden-Clearfield, UT",
        643: "Oklahoma City, OK",
        644: "Olympia-Tumwater, WA",
        645: "Omaha-Council Bluffs, NE-IA",
        646: "Orlando-Kissimmee-Sanford, FL",
        647: "Oshkosh-Neenah, WI",
        648: "Owensboro, KY",
        649: "Oxnard-Thousand Oaks-Ventura, CA",
        650: "Palm Bay-Melbourne-Titusville, FL",
        651: "Panama City, FL",
        652: "Parkersburg-Vienna, WV",
        653: "Pensacola-Ferry Pass-Brent, FL",
        654: "Peoria, IL",
    },
    "YEAR": {
        635: 2016,
        636: 2016,
        637: 2016,
        638: 2016,
        639: 2016,
        640: 2016,
        641: 2016,
        642: 2016,
        643: 2016,
        644: 2016,
        645: 2016,
        646: 2016,
        647: 2016,
        648: 2016,
        649: 2016,
        650: 2016,
        651: 2016,
        652: 2016,
        653: 2016,
        654: 2016,
    },
    "art-LQ_EMPL_ESTAB": {
        635: 0.17904446546830652,
        636: 0.0009460737937559133,
        637: 0.006622516556291391,
        638: 0.0009460737937559133,
        639: 0.0004730368968779564,
        640: 0.0014191106906338694,
        641: 0.0,
        642: 0.0009460737937559133,
        643: 0.0011825922421948912,
        644: 0.00023651844843897819,
        645: 0.002838221381267739,
        646: 0.006622516556291391,
        647: 0.0,
        648: 0.0007095553453169347,
        649: 0.0021286660359508052,
        650: 0.0014191106906338694,
        651: 0.0007095553453169347,
        652: 0.0,
        653: 0.0004730368968779564,
        654: 0.0009460737937559133,
    },
    "fun-LQ_EMPL_ESTAB": {
        635: 1,
        636: 0,
        637: 1,
        638: 0,
        639: 1,
        640: 0,
        641: 1,
        642: 0,
        643: 1,
        644: 0,
        645: 1,
        646: 0,
        647: 1,
        648: 0,
        649: 1,
        650: 0,
        651: 1,
        652: 0,
        653: 1,
        654: 0,
    },
    "HRS_IN_TRAF": {
        635: 6.302025128362779e-05,
        636: 0.8344073516539441,
        637: 0.6787295098899611,
        638: 0.209125991701321,
        639: 0.598465026042049,
        640: 0.268625913994656,
        641: 0.17236144695234898,
        642: 0.4374353916841021,
        643: 0.7217089349745179,
        644: 0.0804077037427359,
        645: 0.917436674794886,
        646: 0.165485594007562,
        647: 0.895035392136478,
        648: 0.6719423883588169,
        649: 0.0845668256799841,
        650: 0.548564507948169,
        651: 0.587657461215386,
        652: 0.738221808086205,
        653: 0.5626545417453399,
        654: 0.8783257440555658,
    },
}


sample2 = {
    "accommodation-LQ_EMPL_ESTAB_RANK": [
        34.0,
        280.0,
        113.0,
        324.0,
        114.0,
        384.0,
        111.0,
        5.0,
        183.0,
        210.0,
        90.0,
        366.0,
        88.0,
        79.0,
        47.0,
        142.0,
        352.0,
        32.0,
        125.0,
        91.0,
        32.0,
        313.0,
        107.0,
        318.0,
        135.0,
        384.0,
        149.0,
        23.0,
        200.0,
        175.0,
        108.0,
        367.0,
        65.0,
        40.0,
        57.0,
        137.0,
        357.0,
        54.0,
        186.0,
        66.0,
    ],
    "accounting_and_taxes-LQ_EMPL_ESTAB_RANK": [
        369.0,
        67.0,
        333.0,
        15.0,
        226.0,
        98.0,
        42.0,
        286.0,
        351.0,
        255.0,
        121.0,
        177.0,
        3.0,
        139.0,
        349.0,
        150.0,
        327.0,
        159.0,
        336.0,
        105.0,
        367.0,
        44.0,
        322.0,
        13.0,
        236.0,
        72.0,
        96.0,
        293.0,
        365.0,
        278.0,
        145.0,
        161.0,
        6.0,
        141.0,
        354.0,
        175.0,
        355.0,
        166.0,
        330.0,
        127.0,
    ],
    "advertising_distribution_services-LQ_EMPL_ESTAB_RANK": [
        374.0,
        70.0,
        322.0,
        166.0,
        284.0,
        70.0,
        70.0,
        274.0,
        179.0,
        202.0,
        253.0,
        354.0,
        70.0,
        70.0,
        177.0,
        167.0,
        277.0,
        290.0,
        336.0,
        206.0,
        368.0,
        66.0,
        348.0,
        258.0,
        227.0,
        66.0,
        66.0,
        272.0,
        178.0,
        156.0,
        248.0,
        362.0,
        66.0,
        66.0,
        184.0,
        203.0,
        322.0,
        361.0,
        346.0,
        197.0,
    ],
    "agriculture-LQ_EMPL_ESTAB_RANK": [
        20.0,
        201.0,
        192.0,
        83.0,
        263.0,
        194.0,
        21.0,
        241.0,
        143.0,
        179.0,
        318.0,
        72.0,
        117.0,
        304.0,
        213.0,
        12.0,
        38.0,
        26.0,
        86.0,
        307.0,
        24.0,
        198.0,
        182.0,
        98.0,
        270.0,
        194.0,
        8.0,
        240.0,
        144.0,
        162.0,
        318.0,
        73.0,
        149.0,
        322.0,
        218.0,
        14.0,
        63.0,
        42.0,
        82.0,
        306.0,
    ],
    "accommodation-PC_ESTAB": [
        0.0031629275468922397,
        0.013849632560768795,
        0.005674797492105624,
        0.014164795301433754,
        0.00869061413673233,
        0.06990801576872538,
        0.007541071909507138,
        0.0041220115416323155,
        0.007929064711399095,
        0.005990016638935108,
        0.006588072122052704,
        0.008485865114213825,
        0.0071530758226037204,
        0.008045977011494253,
        0.004380414679256303,
        0.00667693888032871,
        0.01646090534979424,
        0.006698564593301436,
        0.006653074364202168,
        0.007016292068022357,
        0.003203362226745207,
        0.015927189988623434,
        0.005542642588950474,
        0.013326499231163505,
        0.00844062947067239,
        0.06830031282586027,
        0.00809829656520525,
        0.004836227742360959,
        0.008226974332967062,
        0.006090534979423868,
        0.006987941539903704,
        0.008582195902080628,
        0.006458859870822803,
        0.006466337010270064,
        0.00436241610738255,
        0.0066877606788436645,
        0.0164969450101833,
        0.007707129094412331,
        0.007434944237918215,
        0.006435466571326421,
    ],
    "accounting_and_taxes-PC_ESTAB": [
        0.016662288306275058,
        0.014980214810627475,
        0.017253214955837263,
        0.012782864052513387,
        0.017526071842410198,
        0.010249671484888305,
        0.013735523835173714,
        0.018811361762722027,
        0.019410577770199226,
        0.013976705490848586,
        0.014433079056865462,
        0.017234857828868386,
        0.010014306151645207,
        0.01532567049808429,
        0.02175605957363964,
        0.01599530413089735,
        0.0176954732510288,
        0.014354066985645932,
        0.01802768537396716,
        0.01189202045427518,
        0.01666513132394631,
        0.013936291240045506,
        0.017074915072411944,
        0.01230138390568939,
        0.01759656652360515,
        0.009384775808133471,
        0.015358838313320303,
        0.01839232065655456,
        0.019186881920378658,
        0.014814814814814815,
        0.014274148877242319,
        0.016831871298730088,
        0.010390339792193205,
        0.014834537847090146,
        0.02166826462128476,
        0.016180066158492736,
        0.017515274949083504,
        0.01445086705202312,
        0.016994158258098774,
        0.011798355380765105,
    ],
    "advertising_distribution_services-PC_ESTAB": [
        0.0004290793183768543,
        0.0,
        0.00036611596723262096,
        0.00017274140611504575,
        0.00028968713789107763,
        0.0,
        0.0,
        0.00044967398635988915,
        0.00014209793389604114,
        0.0001663893510815308,
        0.00034674063800277404,
        0.0004604733007712928,
        0.0,
        0.0,
        0.00014601382264187675,
        0.00014674590945777387,
        0.000411522633744856,
        0.00047846889952153117,
        0.000643845906213113,
        0.00023784040908550366,
        0.0004553884446051244,
        0.0,
        0.00031289111389236547,
        0.000341705108491372,
        0.0002861230329041488,
        0.0,
        0.0,
        0.00043965706748735987,
        0.000197221987434142,
        0.0001646090534979424,
        0.0003408751970684733,
        0.000570035152167717,
        0.0,
        0.0,
        0.00019175455417066154,
        0.00021573421544656985,
        0.0006109979633401223,
        0.0004816955684007707,
        0.0007434944237918214,
        0.00023835061375283043,
    ],
    "agriculture-PC_ESTAB": [
        0.001621744689048845,
        0.005087620124364048,
        0.002745869754244657,
        0.002936603903955778,
        0.011297798377752029,
        0.004993429697766097,
        0.0016159439806086725,
        0.004196957206025632,
        0.0031829937192713216,
        0.005657237936772047,
        0.009708737864077669,
        0.0023517029289391025,
        0.004005722460658083,
        0.012260536398467432,
        0.006375936922028619,
        0.0016875779587643995,
        0.0026748971193415643,
        0.0023923444976076554,
        0.003326537182101084,
        0.014865025567843975,
        0.0016060264229585304,
        0.004835039817974972,
        0.002592526372251028,
        0.00341705108491372,
        0.0117310443490701,
        0.0046923879040667365,
        0.0013962580284836634,
        0.0041034659632153605,
        0.003127377229312823,
        0.0049382716049382715,
        0.009374067919383016,
        0.002311809228235741,
        0.004493119910137603,
        0.012552301255230124,
        0.006423777564717161,
        0.0015820509132748455,
        0.003054989816700611,
        0.002408477842003853,
        0.003080191184280404,
        0.014658562745799068,
    ],
    "accommodation-PRES_ESTAB": [
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
    ],
    "accounting_and_taxes-PRES_ESTAB": [
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
    ],
    "advertising_distribution_services-PRES_ESTAB": [
        1.0,
        0.0,
        1.0,
        1.0,
        1.0,
        0.0,
        0.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        0.0,
        0.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        0.0,
        1.0,
        1.0,
        1.0,
        0.0,
        0.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        0.0,
        0.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
    ],
    "agriculture-PRES_ESTAB": [
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
    ],
    "gini_index": [
        0.5098,
        0.4676,
        0.4741,
        0.4336,
        0.433,
        0.4526,
        0.4411,
        0.3994,
        0.4643,
        0.4041,
        0.4425,
        0.4663,
        0.436,
        0.4332,
        0.4433,
        0.4493,
        0.4396,
        0.4572,
        0.441,
        0.4397,
        0.5113,
        0.472,
        0.4765,
        0.4413,
        0.4409,
        0.4646,
        0.4553,
        0.3949,
        0.4624,
        0.4083,
        0.4419,
        0.4666,
        0.4323,
        0.4432,
        0.4456,
        0.4528,
        0.4461,
        0.4589,
        0.4364,
        0.4421,
    ],
    "median_income": [
        67296.0,
        44993.0,
        50921.0,
        66233.0,
        39459.0,
        57637.0,
        57150.0,
        63772.0,
        51461.0,
        61677.0,
        58249.0,
        48768.0,
        52018.0,
        45939.0,
        77348.0,
        48925.0,
        47003.0,
        41693.0,
        49860.0,
        54860.0,
        69211.0,
        45980.0,
        52235.0,
        67574.0,
        40295.0,
        59338.0,
        58335.0,
        65687.0,
        52825.0,
        62854.0,
        59803.0,
        50183.0,
        53501.0,
        46749.0,
        78593.0,
        49914.0,
        47958.0,
        43532.0,
        50563.0,
        56111.0,
    ],
    "median_home_value": [
        398800.0,
        132600.0,
        175100.0,
        244000.0,
        111000.0,
        299700.0,
        103200.0,
        199300.0,
        137200.0,
        239400.0,
        148200.0,
        157900.0,
        143100.0,
        112700.0,
        458100.0,
        142200.0,
        156800.0,
        104900.0,
        135400.0,
        131300.0,
        403300.0,
        137000.0,
        189400.0,
        241500.0,
        114400.0,
        296100.0,
        112300.0,
        206900.0,
        141500.0,
        242900.0,
        152100.0,
        166300.0,
        144300.0,
        116400.0,
        481400.0,
        150500.0,
        160500.0,
        106400.0,
        139000.0,
        133300.0,
    ],
    "total_population": [
        19979950.0,
        155565.0,
        735767.0,
        273185.0,
        336811.0,
        95805.0,
        149557.0,
        623323.0,
        1318408.0,
        262723.0,
        895919.0,
        2277816.0,
        169004.0,
        116342.0,
        840833.0,
        553591.0,
        191138.0,
        92400.0,
        467348.0,
        379947.0,
        20031443.0,
        155134.0,
        751422.0,
        272033.0,
        340341.0,
        95404.0,
        153177.0,
        632793.0,
        1337075.0,
        266311.0,
        904834.0,
        2328508.0,
        169487.0,
        116932.0,
        843110.0,
        560683.0,
        194212.0,
        92088.0,
        473477.0,
        379241.0,
    ],
    "MSA": [
        35620,
        35660,
        35840,
        35980,
        36100,
        36140,
        36220,
        36260,
        36420,
        36500,
        36540,
        36740,
        36780,
        36980,
        37100,
        37340,
        37460,
        37620,
        37860,
        37900,
        35620,
        35660,
        35840,
        35980,
        36100,
        36140,
        36220,
        36260,
        36420,
        36500,
        36540,
        36740,
        36780,
        36980,
        37100,
        37340,
        37460,
        37620,
        37860,
        37900,
    ],
    "YEAR": [
        2015,
        2015,
        2015,
        2015,
        2015,
        2015,
        2015,
        2015,
        2015,
        2015,
        2015,
        2015,
        2015,
        2015,
        2015,
        2015,
        2015,
        2015,
        2015,
        2015,
        2016,
        2016,
        2016,
        2016,
        2016,
        2016,
        2016,
        2016,
        2016,
        2016,
        2016,
        2016,
        2016,
        2016,
        2016,
        2016,
        2016,
        2016,
        2016,
        2016,
    ],
}

data_copy = pd.DataFrame(sample2)


industry_peer_para = [
    [
        35840,
        [2016],
        [
            "accommodation",
            "accounting_and_taxes",
            "advertising_distribution_services",
            "agriculture",
        ],
        [],
        [],
    ]
]
known_industry_peers = [[37340, 35620]]

outcome_peer_para = [
    [37900, [2016], [], ["gini_index", "median_income", "median_home_value"], []]
]
known_outcome_peers = [[36540, 36780]]

industry_ancestral_para = [
    [
        35840,
        [2016],
        [
            "accommodation",
            "accounting_and_taxes",
            "advertising_distribution_services",
            "agriculture",
        ],
        [],
        [2016, 2015],
    ]
]
known_industry_ancestral_peers = [[36740, 35620]]

outcome_ancestral_para = [
    [
        37900,
        [2016],
        [],
        ["gini_index", "median_income", "median_home_value"],
        [2016, 2015],
    ]
]
known_outcome_ancestral_peers = [[36540, 36220]]

general_para = [
    [
        35840,
        [2016],
        [
            "accommodation",
            "accounting_and_taxes",
            "advertising_distribution_services",
            "agriculture",
        ],
        [],
        [2016, 2015],
        "fm",
    ],
    [
        37900,
        [2016],
        [],
        ["gini_index", "median_income", "median_home_value"],
        [2016, 2015],
        "outcome",
    ],
]
known_general_peers = [[37340, 35620], [36100, 36980]]

geographical_para = [35620, [2016]]
geographical_peers = [45940, 14860, 20700, 10900, 35300]

state_para = [35620, [2016]]
state_peers = [
    27780,
    45060,
    11020,
    44300,
    10900,
    15380,
    14100,
    38300,
    49660,
    16540,
    35620,
    36140,
    42540,
    21300,
    27060,
    30140,
    39740,
    40380,
    48700,
    48060,
    12100,
    28740,
    25420,
    46540,
    13780,
    10580,
    24020,
    49620,
    37980,
    20700,
    23900,
    29540,
    45940,
    47220,
    21500,
]

outcome_ancestral_para = [
    [
        37900,
        [2016],
        [],
        ["gini_index", "median_income", "median_home_value"],
        [2016, 2015],
    ]
]
known_outcome_ancestral_peers = [[36540, 36220]]

df_data = pd.read_csv(os.path.join(
    dirname, "../data/processed/metrics_outcomes.csv"))
df_county = pd.read_csv(os.path.join(
    dirname, "../data/processed/county_metrics_outcomes.csv"))
df_msa_def = pd.read_csv(
    os.path.join(dirname, "../data/external/omb_msa_1990_2018.csv")
)
df_county_dist = pd.read_csv(
    os.path.join(
        dirname, "../data/processed/sf12010countydistance500miles.csv")
)


class TestExplorer(unittest.TestCase):
    def test_run(self):
        msa = 35620
        year = 2016
        true_geo_peers = [45940, 14860, 20700, 10900]
        geo_peers, _ = pe.get_geographic_peers(
            df_data, df_county_dist, df_msa_def, msa, 4, year
        )
        self.assertListEqual(true_geo_peers, geo_peers, "Error with Geo peers")

        geo_peers, _ = pe.get_geographic_peers(
            df_county, df_county_dist, df_msa_def, 48059, 4, year, 'county'
        )
        fms_peers, _ = pe.get_peers_from_input(
            df_data,
            msa,
            year,
            6,
            fms=["accounting_and_taxes", "advertising_distribution_services"],
        )
        true_fms_peers = [45300, 41060, 20500, 12060, 26900, 41860]
        self.assertListEqual(true_fms_peers, fms_peers, "Error with fm peers")
        outcomes_peers, _ = pe.get_peers_from_input(
            df_data, msa, year, 8, outcomes=["median_income", "total_population"]
        )
        true_outcomes_peers = [31080, 16980, 19100,
                               26420, 37980, 33100, 12060, 47900]
        self.assertListEqual(
            true_outcomes_peers, outcomes_peers, "Error with ouctome peers"
        )
        true_distinguishing_peers = [
            41860,
            31080,
            14460,
            45940,
            19100,
            37980,
            41620,
            16980,
            12580,
            31700,
        ]
        distinguishing_peers, _ = pe.get_distinguishing_features_peers(
            df_data, msa, year, 10, 10
        )
        self.assertListEqual(
            true_distinguishing_peers,
            distinguishing_peers,
            "Error with distinguishing peers",
        )
        true_top_fms_peers = [
            37980,
            14460,
            38300,
            12580,
            17460,
            40380,
            10580,
            35300,
            20500,
            14860,
            45060,
            45300,
        ]
        top_fms_peers, _ = pe.get_top_n_fms_peers(
            df_data, msa, year, n_peers=12, metric="PC_EMPL", n_fms=10
        )

        self.assertListEqual(
            true_top_fms_peers, top_fms_peers, "Error with top fms peers"
        )

        true_top_fms_peers_lq = [31080, 41860, 32820, 33100,
                                 24660, 14500, 42660, 25980,
                                 47220, 39900, 45940, 20500]

        top_fms_peers_lq, _ = pe.get_top_n_fms_peers(
            df_data, msa, year, n_peers=12, n_fms=10
        )

        self.assertListEqual(
            true_top_fms_peers_lq, top_fms_peers_lq, "Error with top fms peers"
        )

        top_fms_coverage = pe.get_emp_threshold_peers(df_data, msa, year, 10)

        stab_peers, fms = pe.get_stabilizing_peers(
            df_data, msa, year, 10, method="top_fms"
        )

        stab_peers, fms = pe.get_stabilizing_peers(
            df_data, msa, year, 10, method="distinguishing"
        )

        stab_peers, fms = pe.get_stabilizing_peers(
            df_data, msa, year, n_peers=10, method="coverage"
        )

    # TODO Write test with sample data
    """
        def test_top_industries_helper(self):
            sample_df = pd.DataFrame(sample)
            NY = 35620
            test = PeerExplorer(NY, [2016])
            out = test._compute_top_industries_list(
                data=sample_df, n_fms=2, metric='LQ_EMPL_ESTAB')
            expected_tup1 = ('fun', 'art')
            expected_tup2 = ('art', 'fun')
            ans1 = (out[0][0], out[0][1])
            ans2 = (out[1][0], out[1][1])
            self.assertEqual(expected_tup1, ans1)
            self.assertEqual(expected_tup2, ans2)

        def test_strength_weakness(self):
            ## this test needs to be done with sample2 and needs to include PRES_ESTAB as a metric
            sample_df = pd.DataFrame(sample2)
            NY = 35620
            test1 = PeerExplorer(NY, [2016])
            exp_best = [('advertising_distribution_services', 1),
                         ('accounting_and_taxes', 1)]
            exp_worst = [('accommodation', 19)]
            best, worst = test1._find_strengths_weaknesses(sample_df, frac=0.1)
            self.assertEqual(set(exp_best), set(
                best), msg='strengths function has an issue')
            self.assertEqual(set(exp_worst), set(worst),
                             msg='weakness function has an issue')

        def test_top_industries_distances(self):
            NY = 35620
            test = PeerExplorer(NY, [2016])
            curr = ['A', 'B', 'C', 'D']
            peer = ['A', 'C', 'E', 'D']
            expected = 4
            ans = test._compute_top_industries_distances(curr, peer)
            self.assertEqual(expected, ans)

        def test_find_industry_peers(self):
            res = []
            for i, (msa, years, fms, outcomes, year_gap) in enumerate(industry_peer_para):
                lpe = PeerExplorer(msa, years, fms, outcomes, year_gap)
                lpe.compute_distance(data_copy, omb, county_distances)
                res.append(lpe.find_industry_peers(2))
            self.assertEqual(known_industry_peers, res,
                             msg='find_industry_peer function has an issue')

        def test_find_outcome_peers(self):
            res = []
            for i, (msa, years, fms, outcomes, year_gap) in enumerate(outcome_peer_para):
                lpe = PeerExplorer(msa, years, fms, outcomes, year_gap)
                lpe.compute_distance(data_copy, omb, county_distances)
                res.append(lpe.find_outcome_peers(2))
            self.assertEqual(known_outcome_peers, res,
                             msg='find_outcome_peer function has an issue')

        def test_find_industry_ancestral_peers(self):
            res = []
            for i, (msa, years, fms, outcomes, year_gap) in enumerate(industry_ancestral_para):
                lpe = PeerExplorer(msa, years, fms, outcomes, year_gap)
                lpe.compute_distance(data_copy, omb, county_distances)
                res.append(lpe.find_industry_ancestral_peers(2))

            self.assertEqual(known_industry_ancestral_peers, res,
                             msg='find_industry_ancestral_peer function has an issue')

        def test_find_outcome_ancestral_peers(self):
            res = []
            for i, (msa, years, fms, outcomes, year_gap) in enumerate(outcome_ancestral_para):
                lpe = PeerExplorer(msa, years, fms, outcomes, year_gap)
                lpe.compute_distance(data_copy, omb, county_distances)
                res.append(lpe.find_outcome_ancestral_peers(2))

            self.assertEqual(known_outcome_ancestral_peers, res,
                             msg='find_outcome_ancestral_peer function has an issue')

        def test_find_general_peers(self):
            res = []
            for i, (msa, years, fms, outcomes, year_gap, general_metric) in enumerate(general_para):
                lpe = PeerExplorer(msa, years, fms, outcomes,
                                   year_gap, general_metric)
                lpe.compute_distance(data_copy, omb, county_distances)
                res.append(lpe.find_general_peers(2))
            self.assertEqual(known_general_peers, res,
                             msg='find_general_peer function has an issue')

        def test_find_geographic_peers(self):
            lpe = PeerExplorer(geographical_para[0], geographical_para[1])
            lpe.compute_distance(metrics, omb, county_distances)
            self.assertEqual(lpe.find_geographic_peers(
                5), geographical_peers, msg='find_geographic_peers has an issue')
    """


if __name__ == "__main__":
    unittest.main(verbosity=3, exit=False)
