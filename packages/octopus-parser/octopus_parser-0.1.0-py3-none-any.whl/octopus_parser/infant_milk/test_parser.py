
import json

from zooper_parser.infant_milk import parse


def test_parse():
    test_cases = [
        "Morinaga Chil Mil PHP 1+ madu 4x800 grams",
        "Frisolac 1 Gold Susu Bayi - 900gr Tin",
        "RAJASUSU/BEBELOVE 1 Susu Formula Bayi Box 1800g / 1800 g"
    ]

    parse_trees = [
        {
          "company": [
            "Kalbe"
          ],
          "brand": [
            "morinaga",
            "chil mil"
          ],
          "brand_attribute": [
            "php"
          ],
          "age": [
            "1+"
          ],
          "weight": {
              "QUANTITY": "4",
              "WEIGHT_VALUE": "800",
              "WEIGHT_UNIT": "gr"
          },
          "flavor": [
            "madu"
          ],
          "seller": [],
          "text": []
        },
        {
          "company": [
            "FrieslandCampina"
          ],
          "brand": [
            "frisolac"
          ],
          "brand_attribute": [
            "gold",
            "tin"
          ],
          "age": [
            "1"
          ],
          "weight": {
              "WEIGHT_VALUE": "900",
              "WEIGHT_UNIT": "gr"
          },
          "flavor": [],
          "seller": [],
          "text": [
            "susu",
            "bayi",
            "-"
          ]
        },
        {
          "company": [
            "Nutricia"
          ],
          "brand": [
            "bebelove"
          ],
          "brand_attribute": [
            "formula",
            "box"
          ],
          "age": [
            "1"
          ],
          "weight": {
              "WEIGHT_VALUE": "1800",
              "WEIGHT_UNIT": "gr"
          },
          "flavor": [],
          "seller": [
            "rajasusu"
          ],
          "text": [
            "susu",
            "bayi"
          ]
        }
    ]

    for test_case, parse_tree in zip(test_cases, parse_trees):
        actual = parse(test_case)
        assert json.dumps(actual.to_json()) == json.dumps(parse_tree)


def test_canonical():
    test_cases = [
        "Morinaga Chil Mil PHP 1+ madu 4x800 grams",
        "Frisolac 1 Gold Susu Bayi - 900gr Tin",
        "RAJASUSU/BEBELOVE 1 Susu Formula Bayi Box 1800g / 1800 g",
        "Zee Reguler Swizz Chocolate 350gr",
        "MEIJI Step Baby Milk ( 1-3 Years ) - Made In Japan",
        "Milna Toddler Coklat 110 G",
        "Nan Ph Pro 1 400 gram",
        "DANCOW 1+ MADU 800G ADVANCED EXCELNUTRI+ SUSU FORMULA",
        "LACTOGROW 3 Plain Box 750g / 750 g",
        "Susu Dancow 1+, 3+, 5+ 800gr",
        "Susu Nestle Lactogen Premature 400 gram/Susu bayi lactogen premature",
        "Susu Lactogen 1, 750gr",
        "Peptamen junior 400 gram",
        "Susu Nestle Nan 1 pH Pro 800g",
        "Peptamen junior 400 gram",
        "Karihome Step 3 900gram",
        "Nutramigen LGG",
        "Enfamil A+ LactoFree Care Susu Formula Bayi dengan Intoleransi Laktosa",
        "SUSTAGEN Kid 3 Vanila Vanilla Susu Box 350g / 350 g",
        "Enfamil A+1 Susu Formula Bayi - Plain - 800g",
        "SUSTAGEN Kid 3 Vanila Vanilla Susu Box 1200g / 1200 g",
        "Sustagen School 6 + Vanila 800 gram",
        "RAJASUSU/Enfagrow A+ 3 Vanila 800 gr",
        "Enfagrow A+3 Original 800 Gram",
        "Enfamil A+ Tahap 2 Susu Formula Bayi Plain 1800 gr",
        "Enfagrow A+ Tahap 3 1800g 1800gr 1800gram 1800 g gr gram",
        "ENFAGROW A + Gentle Care Susu Pertumbuhan 1-3 Tahun Tin 900g / 900 g",
        "Enfamil A+ Step Up Care Susu Formula Bayi Premature",
        "LACTOGEN LLF khusus Rendah Laktosa 0-12 bulan Box 150g",
        "Similac Advance 2 400 g (6-12 bln) Susu Formula Bayi Lanjutan",
        "TOPFER LACTANA ORGANIC INFANT MILK FORMULA 1",
        "WAKODO Lebens Milk Haihai For Newborn (850gr) - Made In Japan",
        "Susu Ultra Mimi 125ml per dus (40buah)",
        "Susu Ultra Mimi 125.5ml per dus (40 buah)",
        "S26 Promise Gold Tahap 4 1.6 kg",
        "S26 Procal Gold 3 ( 1-3th) 1600g",
        "S26 PROCAL GOLD THP 3 1800GR EXP 2019",
        "Susu S26 LBW GOLD (Susu khusus bayi prematur atau BBLR)",
        "S26 Promil Gold Tahap 2 900gr",
        "S26 Promise Gold 1600gr (Tahap 4) / S-26 susu formula 1.6kg - Can",
        "GLICO Icreo Follow-Up Baby Milk ( 9Months+) - Made In Japan",
        "susu similac hmf untuk bayi prematur",
        "Karihome Goat Milk - Susu Kambing step 4 (3-7thn) 900gram",
        "Susu Kambing Etawa Murni Tanpa Gula",
        "Bellamys organic toddler milk step 3",
        "baby milk jepang glico icreo follow up made in japan TERMURAH buktikan"
    ]

    canonical_strings = [
        "Kalbe / morinaga chil mil php 1+ 4 x 800 gr madu",
        "FrieslandCampina / frisolac gold tin 1 900 gr",
        "Nutricia / bebelove formula box 1 1800 gr",
        "Kalbe / zee swizz reguler 350 gr chocolate",
        "Meiji / meiji step milk 1-3 years",
        "Milna / milna toddler 110 gr chocolate",
        "Nestle / nan ph pro 1 400 gr",
        "Nestle / dancow excelnutri+ advance formula 1+ 800 gr madu",
        "Nestle / lactogrow plain box 3 750 gr",
        "Nestle / dancow 1+ 3+ 5+ 800 gr",
        "Nestle / nestle lactogen premature 400 gr",
        "/ lactogen 1 750 gr",
        "Nestle / peptamen junior 400 gr",
        "Nestle / nestle nan ph pro 1 800 gr",
        "Nestle / peptamen junior 400 gr",
        "Karihome / karihome step 3 900 gr",
        "Mead Johnson / nutramigen lgg",
        "Mead Johnson / enfamil a+ lactofree care formula",
        "Mead Johnson / sustagen kid box 3 350 gr vanilla",
        "Mead Johnson / enfamil a+ formula plain 1 800 gr",
        "Mead Johnson / sustagen kid box 3 1200 gr vanilla",
        "Mead Johnson / sustagen school 6 800 gr vanilla",
        "Mead Johnson / enfagrow a+ 3 800 gr vanilla",
        "Mead Johnson / enfagrow a+ original 3 800 gr",
        "Mead Johnson / enfamil a+ tahap 2 formula plain 1800 gr",
        "Mead Johnson / enfagrow a+ tahap 3 1800 gr",
        "Mead Johnson / enfagrow a+ gentle care tin 1-3 tahun 900 gr",
        "Mead Johnson / enfamil a+ step up care formula premature",
        "Abbott / lactogen llf box 0-12 bulan 150 gr",
        "Abbott / similac advance formula 2 6-12 bln 400 gr",
        "Topfer / topfer lactana organic infant milk formula 1",
        "Wakodo / wakodo lebens haihai milk 850 gr",
        "Ultra Jaya / susu ultra mimi 40 x 125 ml",
        "Ultra Jaya / susu ultra mimi 40 x 125.5 ml",
        "Wyett / s26 promise gold tahap 4 1.6 kg",
        "Wyett / s26 procal gold 3 1-3 1600 gr",
        "Wyett / s26 procal gold 3 2019 1800 gr",
        "Wyett / s26 lbw gold prematur bblr",
        "Wyett / s26 promil gold tahap 2 900 gr",
        "Wyett / s26 promise s-26 gold tahap 4 formula can 1.6 kg",
        "Glico / glico icreo milk 9 months",
        "Abbott / similac hmf prematur",
        "Karihome / karihome goat milk susu kambing step 4 3-7 900 gr",
        "/ susu kambing",
        "/ bellamys organic toddler milk step 3",
        "Glico / glico icreo milk"
    ]

    assert len(test_cases) == len(canonical_strings), "Length of test_cases != canonical_strings"
    for test_case, canonical_string in zip(test_cases, canonical_strings):
        actual = parse(test_case)
        assert actual.to_string() == canonical_string


