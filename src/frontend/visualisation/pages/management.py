from src.frontend.visualisation.pages import avg_interest_rates, debt_to_penny


def page_dict():
    _page_dict = dict()
    _page_dict['/avg_interest_rates'] = avg_interest_rates
    _page_dict['/debt_to_penny'] = debt_to_penny
    return _page_dict
