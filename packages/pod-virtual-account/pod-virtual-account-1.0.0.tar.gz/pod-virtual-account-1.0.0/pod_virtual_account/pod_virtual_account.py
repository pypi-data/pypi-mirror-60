# coding=utf-8
import json
from os import path
from pod_base import PodBase, calc_offset, PodException, ConfigException, InvalidDataException

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


class PodVirtualAccount(PodBase):

    def __init__(self, api_token, token_issuer="1", server_type="sandbox", config_path=None,
                 sc_api_key="", sc_voucher_hash=None):
        here = path.abspath(path.dirname(__file__))
        self._services_file_path = path.join(here, "services.json")
        super(PodVirtualAccount, self).__init__(api_token, token_issuer, server_type, config_path, sc_api_key,
                                                sc_voucher_hash, path.join(here, "json_schema.json"))

    def __get_private_call_address(self):
        """
        دریافت آدرس سرور پرداخت از فایل کانفیگ

        :return: str
        :raises: :class:`ConfigException`
        """
        private_call_address = self.config.get("private_call_address", self._server_type)
        if private_call_address:
            return private_call_address

        raise ConfigException("config `private_call_address` in {} not found".format(self._server_type))

    def add_withdraw_rule_plan(self, subscription_days, max_amount, max_count, type_code, **kwargs):
        """
        ایجاد طرح تعرفه برای مجوز برداشت از حساب مشتری توسط کسب و کار

        :param float subscription_days: تعداد روز اشتراک
        :param float max_amount: سقف مبلغ قابل برداشت توسط کسب و کار
        :param float max_count: سقف مجاز تعداد دفعات برداشت از حساب توسط کسب و کار
        :param str type_code: نوع مجوز برداشت
        :return: dict
        """
        kwargs["subscriptionDays"] = subscription_days
        kwargs["maxAmount"] = max_amount
        kwargs["maxCount"] = max_count
        kwargs["typeCode"] = type_code
        self._validate(kwargs, "addWithdrawRulePlan")

        return self._request.call(
            super(PodVirtualAccount, self)._get_sc_product_settings("/nzh/biz/addWithdrawRulePlan"),
            params=kwargs, headers=self._get_headers(), **kwargs)

    def withdraw_rule_plan_list(self, business_id, page=1, size=50, access_token=None, **kwargs):
        """
        لیست طرح های تعرفه کسب و کار برای مجوز های برداشت از حساب مشتری

        :param int business_id: شناسه کسب و کار
        :param int page: شماره صفحه
        :param int size: تعداد رکورد در هر صفحه
        :param str access_token:  اکسس توکن کاربر - در صورتی که ارسال نشود توکن کسب و کار ارسال می شود
        :return: list of dict
        """
        kwargs["offset"] = calc_offset(page, size)
        kwargs["size"] = size
        kwargs["businessId"] = business_id
        self._validate(kwargs, "withdrawRulePlanList")

        headers = self._get_headers()
        if access_token is not None:
            headers["_token_"] = access_token

        return self._request.call(super(PodVirtualAccount, self)._get_sc_product_settings("/nzh/withdrawRulePlanList"),
                                  params=kwargs, headers=headers, **kwargs)

    def get_link_issue_withdraw_rule_by_plan(self, business_id, plan_id=None, redirect_uri=None, call_uri=None):
        """
        دریافت لینک انتقال به صفحه دریافت مجوز برداشت از مشتری

        :param int business_id:  شناسه کسب و کار
        :param int plan_id:  شناسه طرح
        :param str redirect_uri: آدرس بازگشت
        :param str call_uri:  آدرس فراخوانی سرویس
        :return: str
        """
        params = {
            "businessId": business_id
        }

        if plan_id is not None:
            params["planId"] = plan_id

        if redirect_uri is not None:
            params["redirectUri"] = redirect_uri

        if call_uri is not None:
            params["callUri"] = call_uri

        self._validate(params, "issueWithdrawRuleByPlan")
        return "{}/v1/pbc/issueWithdrawRuleByPlan/?{}".format(self.__get_private_call_address(), urlencode(params))

    def granted_withdraw_rule_list(self, page=1, size=50, **kwargs):
        """
        دریافت لیست مجوزهایی که یک کسب و کار از کاربران برای برداشت از حساب دریافت کرده است

        :param int page: شماره صفحه
        :param int size: تعداد خروجی در هر صفحه
        :return: list of dict
        """
        kwargs["offset"] = calc_offset(page, size)
        kwargs["size"] = size

        self._validate(kwargs, "withdrawRuleList")

        return self._request.call(super(PodVirtualAccount, self)._get_sc_product_settings("/nzh/biz/withdrawRuleList"),
                                  params=kwargs, headers=self._get_headers(), **kwargs)

    def revoke_withdraw_rule(self, rule_id, **kwargs):
        """
        لغو مجوز برداشت از حساب توسط کسب و کار

        :param int rule_id: شناسه مجوز دریافت شده از کاربر
        :return: boolean
        """
        kwargs["ruleId"] = rule_id

        self._validate(kwargs, "revokeWithdrawRule")

        return self._request.call(
            super(PodVirtualAccount, self)._get_sc_product_settings("/nzh/biz/revokeWithdrawRule", method_type="post"),
            params=kwargs, headers=self._get_headers(), **kwargs)

    def withdraw_rule_usage_report(self, rule_id, access_token, **kwargs):
        """
        گزارش استفاده کسب و کار از مجوز برداشت از حساب را به مشتری می دهد

        :param int rule_id: شناسه مجوز دریافت شده از کاربر
        :param str access_token:  اکسس توکن کاربر - در صورتی که ارسال نشود توکن کسب و کار ارسال می شود
        :return: boolean
        """
        kwargs["ruleId"] = rule_id
        kwargs["access_token"] = access_token

        self._validate(kwargs, "withdrawRuleUsageReport")
        del kwargs["access_token"]

        headers = self._get_headers()
        headers["_token_"] = access_token

        return self._request.call(
            super(PodVirtualAccount, self)._get_sc_product_settings("/nzh/withdrawRuleUsageReport"),
            params=kwargs, headers=headers, **kwargs)
