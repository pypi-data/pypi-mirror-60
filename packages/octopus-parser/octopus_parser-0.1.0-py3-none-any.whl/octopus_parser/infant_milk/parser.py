"""Baby milk parser.

Parse baby milk brand from a sentence.
"""
import click
import json

from lark import Lark, Transformer
from lark.lexer import Token

parser = Lark(r"""
    query: (seller "/")* brand_title

    seller: PHRASE | TERM

    brand_title: (brand_term | brand_attribute | flavor | weight_or_age | text | _PUNCT)+
    brand_attribute.1: BRAND_ATTRIBUTE

    flavor: CHOCO
        | HONEY
        | STRAWBERRY
        | VANILLA
        | OTHER_FLAVOR
    
    CHOCO: "chocolate"
        | "choco" 
        | "cokelat"
        | "coklat"
    HONEY: "honey"
        | "madu"
    STRAWBERRY: "strawberry"
        | "soya" 
    VANILLA: "vanilla"
        | "vanila"
    OTHER_FLAVOR: "full cream"
        | "soya"
        | "soy"

    weight_or_age: weight
        | quantity_with_unit
        | age

    age.1: AGE AGE_UNIT* "+"?
    AGE: "(" DIGIT "-" DIGIT ")"
        | DIGIT+ "-" DIGIT+
        | DIGIT+ "+"
        | DIGIT+
    AGE_UNIT: "bulan"
        | "bln"
        | "months"
        | "month"
        | "tahun"
        | "years"
        | "year"

    quantity_with_unit.2: /\d+/ _QUANTITY_UNIT
    _QUANTITY_UNIT: "buah" | "unit"
    quantity: /\d+/

    weight: weight_value weight_unit
        | quantity "x" weight_value weight_unit
    weight_value.2: WEIGHT_VALUE fraction*

    WEIGHT_VALUE: /\d+/

    fraction: FRACTION
    FRACTION: "." DIGIT+

    weight_unit: GRAM | KILO | LB | ML | OZ
    GRAM: "grams"
        | "gram"
        | "grm"
        | "gr"
        | "g"
    KILO: "kg"
        | "kilos"
        | "kilo"
    LB: "lbs"
        | "lb"
    ML: "ml"
    OZ: "oz"

    text.0: PHRASE | TERM

    brand_term.3: abbott_brand
        | anmum_brand
        | arla_foods_brand
        | bellamys_organic_brand
        | earth_organic_brand
        | friesland_brand
        | frisian_flag_brand
        | glico_brand
        | karihome_brand
        | matilde_vicenzi_brand
        | mead_johnson_brand
        | milna_brand
        | kalbe_brand
        | meiji_brand
        | nestle_brand
        | nutricia_brand
        | on_brand
        | ordesa_brand
        | sgm_brand
        | tempo_scan_brand
        | topfer_brand
        | ultra_jaya_brand
        | wakodo_brand
        | wyett_brand

    abbott_brand: ABBOTT_BRAND+
    ABBOTT_BRAND: "isomil"
        | "lactogen llf"
        | "neosure"
        | "pediasure"
        | "triplesure"
        | "similac"
        | "gainkid"

    anmum_brand: ANMUM_BRAND+
    ANMUM_BRAND: "anmum"
        | "materna"

    arla_foods_brand: ARLA_FOODS_BRAND+
    ARLA_FOODS_BRAND: "arla baby & me"

    bellamys_organic_brand: BELLAMYS_ORGANIC_BRAND+
    BELLAMYS_ORGANIC_BRAND: "bellamys toddler"

    earth_organic_brand: EARTH_ORGANIC_BRAND+
    EARTH_ORGANIC_BRAND: "susu almond bubuk"

    frisian_flag_brand: FRISIAN_FLAG_BRAND+
    FRISIAN_FLAG_BRAND: "frisian flag"
        | "frisian"

    friesland_brand: FRIESLAND_BRAND+
    FRIESLAND_BRAND: "frisolac"
        | "friso"

    glico_brand: GLICO_BRAND+
    GLICO_BRAND: "glico"
        | "icreo"

    kalbe_brand: KALBE_BRAND+
    KALBE_BRAND: "bmt"
        | "chilkid"
        | "chil go"
        | "chil kid"
        | "chil school"
        | "chilschool"
        | "chil mil"
        | "chilmil"
        | "entrakid"
        | "moricare"
        | "moricare+"
        | "morinaga"
        | "prodiges"
        | "hagukumi"
        | "zee"
        | "swizz"

    karihome_brand: KARIHOME_BRAND+
    KARIHOME_BRAND: "karihome step"
        | "karihome"

    matilde_vicenzi_brand: MATILDA_VICENZI_BRAND+
    MATILDA_VICENZI_BRAND: "ladyfinger"
        | "vicenzovo"

    mead_johnson_brand: MEAD_JOHNSON_BRAND+
    MEAD_JOHNSON_BRAND: /a\s?\+/
        | "enfamil"
        | "enfagrow"
        | "mead johnson"
        | "meadjohnson"
        | "nutramigen"
        | "pregestimil"
        | "sustagen"

    meiji_brand: MEIJI_BRAND+
    MEIJI_BRAND: "meiji"

    milna_brand: MILNA_BRAND+
    MILNA_BRAND: "milna toddler"

    nestle_brand: NESTLE_BRAND+
    NESTLE_BRAND: "nestle"
        | "cerelac"
        | "dancow"
        | "excelnutri+"
        | "excelnutri"
        | "gerber"
        | "lactogrow"
        | "nan"
        | "naturnes"
        | "nutren"
        | "peptamen"

    nutricia_brand: NUTRICIA_BRAND+
    NUTRICIA_BRAND: "bebelac"
        | "bebelove"
        | "infatrini"
        | "lcp"
        | "neocate"
        | "nutricia"
        | "nutridrink"
        | "nutrilon"
        | "nutribaby"

    on_brand: ON_BRAND+
    ON_BRAND: "on"
        | "hydrolized"
        | "hydro"
        | "whey"

    ordesa_brand: ORDESA_BRAND+
    ORDESA_BRAND: "blemil"
        | "kids"

    nutrigold_brand: NUTRIGOLD_BRAND+
    NUTRIGOLD_BRAND: "nutrigold"

    sgm_brand: SGM_BRAND+
    SGM_BRAND: "eksplor"
        | "llm+"
        | "llm"
        | "1plus"
        | "presinutri"
        | "sgm"
        | "ananda"
        | "phpro"

    tempo_scan_brand: TEMPO_SCAN_BRAND+
    TEMPO_SCAN_BRAND: "nutriplex"
        | "vidoran"
        | "xmart"

    topfer_brand: TOPFER_BRAND+
    TOPFER_BRAND: "topfer"
        | "lactana"

    ultra_jaya_brand: ULTRA_JAYA_BRAND+
    ULTRA_JAYA_BRAND: "susu ultra"

    wakodo_brand: WAKODO_BRAND+
    WAKODO_BRAND: "wakodo"
        | "gungun"
        | "haihai"
        | "lebens"

    wyett_brand: WYETT_BRAND+

    WYETT_BRAND: "procal"
        | "s-26"
        | "s26"
        | "promise"
        | "promil"
        | "lbw"

    BRAND_ATTRIBUTE: "advance"
        | "bblr"
        | "bellamys"
        | "blenuten"
        | "box"
        | "complete"
        | "formula"
        | "hmf"
        | "jelajah"
        | "junior"
        | "gain"
        | "goat"
        | "gold"
        | "infant"
        | "junior"
        | "kids"
        | "kidz"
        | "kid"
        | "lactofree"
        | "lactogen"
        | "lgg"
        | "milk"
        | "mimi"
        | "optimum"
        | "organic"
        | "original"
        | "php"
        | "ph-p"
        | "ph"
        | "plain"
        | "platinum"
        | "plus"
        | "premature"
        | "prematur"
        | "premium"
        | "protein"
        | "pro"
        | "promise"
        | "reguler"
        | "regular"
        | "royal"
        | "school"
        | "step up"
        | "step"
        | "susu kambing"
        | /tahap\s?\d+/
        | "toddler"
        | "triple"
        | "can"
        | "tin"
        | "gentle"
        | "care"
        | "Σ"
        | "zigma"

    TERM    : (LCASE_LETTER|UCASE_LETTER|DIGIT|SYMBOL)+
    PHRASE  : /".*?(?<!\\)"|'.*?(?<!\\)'/
    SYMBOL  : /[-+?_~`!@#$%^*=:;',\.]/
    _PUNCT  : "/" | "\\" | "," | ";" | "(" | ")" | "&" | "|" | "[" | "]"
        | /[u"\u007e-\uffff"]/

    %import common.WORD
    %import common.DIGIT
    %import common.LCASE_LETTER
    %import common.UCASE_LETTER
    %import common.SIGNED_NUMBER     -> NUMBER
    %import common.WS
    %ignore WS

    """, start='query')


class _ASTNode:
    """Abstract Syntax Tree node."""
    def __init__(self, sid, name, leaf, operands):
        self.sid = sid
        self.name = name
        self.leaf = leaf
        self.operands = operands

    def __repr__(self):
        return '<' + self.name + ':' + str(self.sid) + '>'


class _InternalNode(_ASTNode):
    def __init__(self, sid, operands):
        super(_InternalNode, self).__init__(sid, 'InternalRoot', leaf=False, operands=operands)


class _LeafNode(_ASTNode):
    def __init__(self, sid, operands):
        super(_LeafNode, self).__init__(sid, 'LeafNode', leaf=True, operands=operands)

    def __repr__(self):
        return '<' + self.name + ':' + str(self.sid) + ':`' + self.operands[0] + '`>'


class T(Transformer):
    """Parse tree transformer.

    Transforms the parse tree into AST.
    """
    def __init__(self):
        self.sid = 0
        self.company = {}
        self.company = {}
        self.brand_terms = {}
        self.brand_attributes = {}
        self.flavors = {}
        self.weights = {}
        self.ages = {}
        self.sellers = {}
        self.texts = {}

    def query(self, args):
        self.sid += 1
        # print('query:({})'.format(args))
        return _InternalNode(self.sid, args)

    def seller(self, args):
        self.sid += 1
        self.sellers[args[0].value] = 1
        return _InternalNode(self.sid, args)

    def normalize_brand_term(self, term):
        """Apply some normalization to brand term."""
        if term == 'a +':
            return 'a+'
        return term

    def brand_term(self, args):
        self.sid += 1
        # print('brand_term:({})'.format(args))

        _company = args[0].data
        if _company == 'abbott_brand':
            self.company['abbott'] = 'Abbott'
        elif _company == 'anmum_brand':
            self.company['anmum'] = 'Anmum'
        elif _company == 'arla_foods_brand':
            self.company['arla_foods'] = 'Arla Foods'
        elif _company == 'bellamys_organic_brand':
            self.company['bellamys'] = 'Bellamys Organic'
        elif _company == 'earth_organic_brand':
            self.company['earth_organic'] = 'Earth Organic'
        elif _company == 'friesland_brand':
            self.company['friesland'] = 'FrieslandCampina'
        elif _company == 'frisian_flag_brand':
            self.company['frisian_flag'] = 'Frisian Flag'
        elif _company == 'matilde_vicenzi_brand':
            self.company['matilde_vicenzi'] = 'Matilde Vicenzi'
        elif _company == 'mead_johnson_brand':
            self.company['mead_johnson'] = 'Mead Johnson'
        elif _company == 'milna_brand':
            self.company['milna'] = 'Milna'
        elif _company == 'glico_brand':
            self.company['glico'] = 'Glico'
        elif _company == 'karihome_brand':
            self.company['karihome'] = 'Karihome'
        elif _company == 'kalbe_brand':
            self.company['kalbe'] = 'Kalbe'
        elif _company == 'meiji_brand':
            self.company['meiji'] = 'Meiji'
        elif _company == 'nestle_brand':
            self.company['nestle'] = 'Nestle'
        elif _company == 'nutricia_brand':
            self.company['nutricia'] = 'Nutricia'
        elif _company == 'on_brand':
            self.company['on'] = 'ON'
        elif _company == 'ordesa_brand':
            self.company['ordesa'] = 'Ordesa'
        elif _company == 'sgm_brand':
            self.company['sgm'] = 'SGM'
        elif _company == 'tempo_scan_brand':
            self.company['tempo_scan'] = 'Tempo Scan'
        elif _company == 'topfer_brand':
            self.company['topfer'] = 'Topfer'
        elif _company == 'ultra_jaya_brand':
            self.company['ultra_jaya'] = 'Ultra Jaya'
        elif _company == 'wakodo_brand':
            self.company['wakodo'] = 'Wakodo'
        elif _company == 'wyett_brand':
            self.company['wyett'] = 'Wyett'

        for t in args[0].children:
            brand_term = self.normalize_brand_term(t.value)
            self.brand_terms[brand_term] = 1
        return _InternalNode(self.sid, args)

    def brand_attribute(self, args):
        self.sid += 1
        # print('brand_attribute:({})'.format(args))
        self.brand_attributes[args[0]] = 1
        return _InternalNode(self.sid, args)

    def normalize_flavor(self, _type, value):
        """Normalize flavor into canonical flavor value."""
        if _type == 'CHOCO':
            return 'chocolate'
        elif _type == 'HONEY':
            return 'madu'
        elif _type == 'STRAWBERRY':
            return 'strawberry'
        elif _type == 'VANILLA':
            return 'vanilla'
        return value

    def flavor(self, args):
        self.sid += 1
        # print('flavor:({})'.format(args))
        flavor = self.normalize_flavor(args[0].type, args[0].value)
        self.flavors[flavor] = 1
        return _InternalNode(self.sid, args)

    def normalize_weight(self, _type, value):
        """Normalize the weight unit.
        
        If the _type is one of the weight unit, normalize the value to canonical symbol.
        """
        if _type == 'GRAM':
            return 'WEIGHT_UNIT', 'gr'
        elif _type == 'KILO':
            return 'WEIGHT_UNIT', 'kg'
        elif _type == 'OZ':
            return 'WEIGHT_UNIT', 'oz'
        elif _type == 'LB':
            return 'WEIGHT_UNIT', 'lb'
        elif _type == 'ML':
            return 'WEIGHT_UNIT', 'ml'
        return _type, value

    def quantity_with_unit(self, args):
        self.sid += 1
        self.weights["QUANTITY"] = args[0].value
        return _InternalNode(self.sid, args)

    def quantity(self, args):
        self.sid += 1
        self.weights["QUANTITY"] = args[0].value
        return _InternalNode(self.sid, args)

    def weight_value(self, args):
        self.sid += 1
        t = args[0]
        _type, _value = self.normalize_weight(t.type, t.value)
        self.weights[_type] = _value
        return _InternalNode(self.sid, args)

    def weight_unit(self, args):
        self.sid += 1
        _type, _value = self.normalize_weight(args[0].type, args[0].value)
        self.weights[_type] = _value
        return _InternalNode(self.sid, args)

    def fraction(self, args):
        self.sid += 1
        self.sid += 1
        self.weights[args[0].type] = args[0].value
        return _InternalNode(self.sid, args)

    def age(self, args):
        self.sid += 1
        # print('age:({})'.format(args[0].value))
        for arg in args:
            self.ages[arg.value] = 1
        return _InternalNode(self.sid, args)

    def text(self, args):
        self.sid += 1
        self.texts[args[0]] = 1
        # print('text:({})'.format(args))
        return _LeafNode(self.sid, args)

    def to_json(self):
        """Returns brand as dictionary."""
        data = dict()
        data['company'] = list(self.company.values())
        data['brand'] = list(self.brand_terms.keys())
        data['brand_attribute'] = list(self.brand_attributes.keys())
        data['age'] = list(self.ages.keys())
        data['weight'] = self.weights
        data['flavor'] = list(self.flavors.keys())
        data['seller'] = list(self.sellers.keys())
        data['text'] = list(self.texts.keys())
        return data

    def to_string(self):
        """Returns brand canonical string."""
        tokens = []
        tokens.extend(list(self.company.values()))
        tokens.append('/')
        if len(self.brand_terms.keys()):
            tokens.extend(list(self.brand_terms.keys()))
        if len(self.brand_attributes.keys()):
            tokens.extend(list(self.brand_attributes.keys()))
        if len(self.ages.keys()):
            tokens.extend(list(self.ages.keys()))
        if self.weights.get('QUANTITY'):
            tokens.append(self.weights['QUANTITY'])
            tokens.append('x')
        weight_value = 0.0
        if self.weights.get('WEIGHT_VALUE'):
            weight_value = float(self.weights['WEIGHT_VALUE'])
        if self.weights.get('FRACTION'):
            weight_value += float(self.weights['FRACTION'])
        if weight_value > 0.0:
            if weight_value - int(weight_value) > 0:
                tokens.append(str(weight_value))
            else:
                tokens.append(str(int(weight_value)))
        if self.weights.get('WEIGHT_UNIT'):
            tokens.append(self.weights['WEIGHT_UNIT'])
        if len(self.flavors) > 0:
            tokens.extend(list(self.flavors.keys()))
        return " ".join(tokens)


def parse(sentence, pretty_print=False):
    sentence = sentence.lower()
    # print('Sentence: `{}`'.format(sentence))
    parse_tree = parser.parse(sentence)
    if pretty_print:
        print(parse_tree.pretty())
    t = T()
    t.transform(parse_tree)
    return t


@click.command()
@click.argument('sentence')
@click.option('--format', help='Output format ["json", "text"]', default='json')
@click.option('--pretty/--no-pretty', help='Print pretty parse tree.', default=False)
def cli_parse(sentence, format, pretty):
    t = parse(sentence, pretty)
    if format == 'json':
        print(json.dumps(t.to_json(), indent=2))
    else:
        print(t.to_string())


if __name__ == '__main__':
    cli_parse()

