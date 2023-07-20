from decimal import Decimal

class EngNum():
    """ Used for easy manipulation of numbers which use engineering notation """
    def __init__(self, value, precision=2):
        """ 
        value: str, int, float, Decimal
        precision: int
        """
        self.precision = precision
        self.unknown = False
        if str(value).lower() in ['none', 'nan']:
            self.unknown_num(value)
        elif isinstance(value, str):
            try:
                self.number = Decimal(value)
            except:
                if value[0] not in '-0123456789':
                    self.unknown_num(value)
                    return
                suffix_keys = [key for key in self._suffix_lookup().keys() if key != '']
                for suffix in suffix_keys:
                    if suffix in value:
                        value = value[:-1] + self._suffix_lookup()[suffix]
                        self.number = Decimal(value)
                        break
                else:
                    self.unknown_num(value)
        elif isinstance(value, int) or isinstance(value, float):
            self.number = Decimal(str(value))
        elif isinstance(value, Decimal):
            self.number = value

    def unknown_num(self, num):
        self.unknown = True
        self.number = num

    def __repr__(self):
        if self.unknown:
            return str(self.number)
        # since Decimal only converts number that are very small into engineering notation
        # so just simply make all number a small number and take advantage of Decimal
        num_str = self.number * Decimal('10e-25')
        num_str = num_str.to_eng_string().lower()
        base, exponent = num_str.split('e')
        base = str(round(Decimal(base), self.precision))
        if base.count('.') == 1 and all('0' in i for i in base.split('.')[1]):
            base = base.split('.')[0]
        if exponent in self._exponent_lookup_scaled():
            return base + self._exponent_lookup_scaled()[exponent]
        num_str = self.number.to_eng_string().lower()
        return num_str

    def _suffix_lookup(self):
        return {'y': 'e-24', 'z': 'e-21', 'a': 'e-18',
                'f': 'e-15', 'p': 'e-12', 'n': 'e-9',
                'u': 'e-6', 'm': 'e-3',
                '':  'e0',
                'k': 'e3', 'M': 'e6', 'G': 'e9', 'T': 'e12'}

    def _exponent_lookup_scaled(self):
        return {'-48': 'y', '-45': 'z', '-42': 'a',
                '-39': 'f', '-36': 'p', '-33': 'n', '-30': 'u', '-27': 'm',
                '-24': '',
                '-21': 'k', '-18': 'M', '-15': 'G', '-12': 'T'}

    def __gt__(self, other):
        return self.number > other.number
    def __lt__(self, other):
        return self.number < other.number
    def __ge__(self, other):
        return self.number >= other.number
    def __le__(self, other):
        return self.number <= other.number
    def __eq__(self, other):
        return self.number == other.number
    def __ne__(self, other):
        return self.number != other.number