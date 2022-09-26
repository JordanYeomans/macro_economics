from src.frontend.visualisation.pages import avg_interest_rates, debt_to_penny, yield_curve


def page_dict():
    _page_dict = dict()
    _page_dict['/avg_interest_rates'] = avg_interest_rates
    _page_dict['/debt_to_penny'] = debt_to_penny
    _page_dict['/yield_curve'] = yield_curve
    return _page_dict
