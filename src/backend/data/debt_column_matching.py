

def get_debt_matching_dict():

    _dict = dict()

    _dict['T-Bonds'] = dict()
    _dict['T-Bonds']['fiscaldata'] = 'Treasury Bonds'
    _dict['T-Bonds']['hometreasury'] = 'Bonds'

    _dict['T-Notes'] = dict()
    _dict['T-Notes']['fiscaldata'] = 'Treasury Notes'
    _dict['T-Notes']['hometreasury'] = 'Notes'

    _dict['T-Bills'] = dict()
    _dict['T-Bills']['fiscaldata'] = 'Treasury Bills'
    _dict['T-Bills']['hometreasury'] = 'Bills'

    _dict['TIPS'] = dict()
    _dict['TIPS']['fiscaldata'] = 'Treasury Inflation-Protected Securities (TIPS)'
    _dict['TIPS']['hometreasury'] = 'Treasury Inflation-Protected Securities'

    return _dict
