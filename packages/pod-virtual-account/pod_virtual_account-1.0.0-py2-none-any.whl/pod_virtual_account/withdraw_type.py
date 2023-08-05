# coding=utf-8


class WithdrawRuleType:
    def __init__(self):
        pass

    """ اشتراک زماندار بدون محدودیت در مبلغ و تعداد دفعات برداشت """
    SUBSCRIPTION = "WITHDRAW_RULE_TYPE_SUBSCRIPTION"

    """ اشتراک زماندار با سقف مبلغ و بدون محدودیت در تعداد دفعات برداشت """
    SUBSCRIPTION_AMOUNT = "WITHDRAW_RULE_TYPE_SUBSCRIPTION_AMOUNT"

    """ اشتراک زماندار با سقف مبلغ و تعداد دفعات محدود """
    SUBSCRIPTION_AMOUNT_COUNT = "WITHDRAW_RULE_TYPE_SUBSCRIPTION_AMOUNT_COUNT"

    """ اشتراک با سقف مبلغ و تعداد دفعات محدود و زمان نا محدود """
    AMOUNT_COUNT = "WITHDRAW_RULE_TYPE_AMOUNT_COUNT"

    """ اشتراک با سقف مبلغ محدود، زمان و تعداد دفعات نامحدود """
    AMOUNT = "WITHDRAW_RULE_TYPE_AMOUNT"
