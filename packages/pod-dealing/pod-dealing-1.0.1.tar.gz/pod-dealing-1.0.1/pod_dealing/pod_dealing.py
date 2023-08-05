# coding=utf-8
from os import path
from pod_base import PodBase, calc_offset


def split_str_to_list(text, sep=","):
    """
    یک رشته را با جدا کننده، جدا می کند و به صورت لیست برمیگرداند

    :param str text: متن
    :param str sep: جدا کننده
    :return: list
    """
    return map(text.strip, text.split(sep))


class PodDealing(PodBase):

    def __init__(self, api_token, token_issuer="1", server_type="sandbox", config_path=None,
                 sc_api_key="", sc_voucher_hash=None):
        here = path.abspath(path.dirname(__file__))
        self._services_file_path = path.join(here, "services.json")
        super(PodDealing, self).__init__(api_token, token_issuer, server_type, config_path, sc_api_key, sc_voucher_hash,
                                         path.join(here, "json_schema.json"))

    def add_dealer(self, dealer_biz_id, all_product_allow=None, **kwargs):
        """
        اجازه ثبت فاکتور برای کسب و کار همکار

        :param int dealer_biz_id:
        :param boolean all_product_allow:
        :return: dict
        """
        params = {
            "dealerBizId": dealer_biz_id
        }

        if all_product_allow is not None:
            params["allProductAllow"] = all_product_allow

        self._validate(params, "addDealer")
        return self._request.call(super(PodDealing, self)._get_sc_product_settings("/nzh/biz/addDealer",
                                                                                   method_type="post"),
                                  params=params, headers=self._get_headers(), **kwargs)

    def dealer_list(self, page=1, size=50, **kwargs):
        """
        لیست کسب و کارهای همکار

        :param int page: شماره صفحه
        :param int size: تعداد رکورد در هر صفحه
        :return: list
        """
        kwargs["offset"] = calc_offset(page, size)
        kwargs["size"] = size

        self._validate(kwargs, "dealerList")
        return self._request.call(super(PodDealing, self)._get_sc_product_settings("/nzh/biz/dealerList"),
                                  params=kwargs, headers=self._get_headers(), **kwargs)

    def enable_dealer(self, dealer_biz_id, **kwargs):
        """
        فعال سازی مجوز فروش، توسط همکاران

        :param int dealer_biz_id:  شناسه کسب و کار همکار
        :return: dict
        """
        params = {"dealerBizId": dealer_biz_id}

        self._validate(params, "enableDealer")

        return self._request.call(super(PodDealing, self)._get_sc_product_settings("/nzh/biz/enableDealer",
                                                                                   method_type="post"),
                                  params=params, headers=self._get_headers(), **kwargs)

    def disable_dealer(self, dealer_biz_id, **kwargs):
        """
        غیرفعال سازی مجوز فروش، توسط همکاران

        :param int dealer_biz_id:  شناسه کسب و کار همکار
        :return: dict
        """
        params = {"dealerBizId": dealer_biz_id}

        self._validate(params, "disableDealer")

        return self._request.call(super(PodDealing, self)._get_sc_product_settings("/nzh/biz/disableDealer",
                                                                                   method_type="post"),
                                  params=params, headers=self._get_headers(), **kwargs)

    def business_dealing_list(self, page=1, size=50, **kwargs):
        """
        لیست کسب و کار های که برایشان مجوز فروش دارید

        :param int page: شماره صفحه
        :param int size: تعداد در هر صفحه
        :return: list
        """
        kwargs["offset"] = calc_offset(page, size)
        kwargs["size"] = size

        self._validate(kwargs, "businessDealingList")

        return self._request.call(
            super(PodDealing, self)._get_sc_product_settings("/nzh/biz/businessDealingList", method_type="post"),
            params=kwargs, headers=self._get_headers(), **kwargs)

    def add_user_and_business(self, username, agent_cellphone_number, agent_last_name, agent_first_name, description,
                              email, guild_code, business_name, country, state, city, address, **kwargs):
        """
        ثبت کسب و کار

        :param str username: نام کاربری - باید یکتا و فقط با حروف انگلیسی و بدون فاصله باشد
        :param str agent_cellphone_number: شماره موبایل نماینده
        :param str agent_last_name: نام نماینده
        :param str agent_first_name: نام خانوادگی نماینده
        :param str description: توضیحات
        :param str email: ایمیل
        :param list guild_code: لیستی از کد اصناف
        :param str business_name: نام کسب و کار
        :param str country: کشور محل کسب و کار
        :param str state: استان محل کسب و کار
        :param str city: شهر محل کسب و کار
        :param str address: آدرس محل کسب و کار

        :return: dict
        """
        kwargs["username"] = username
        kwargs["agentCellphoneNumber"] = agent_cellphone_number
        kwargs["agentLastName"] = agent_last_name
        kwargs["agentFirstName"] = agent_first_name
        kwargs["description"] = description
        kwargs["email"] = email
        kwargs["address"] = address
        kwargs["businessName"] = business_name
        kwargs["country"] = country
        kwargs["state"] = state
        kwargs["city"] = city

        if type(guild_code) == list:
            kwargs["guildCode"] = guild_code
        else:
            kwargs["guildCode"] = [guild_code]

        self._validate(kwargs, "addUserAndBusiness")

        if "tags" in kwargs:
            kwargs["tags"] = split_str_to_list(kwargs["tags"])

        if "tagTrees" in kwargs:
            kwargs["tagTrees"] = split_str_to_list(kwargs["tagTrees"])

        kwargs["guildCode[]"] = kwargs["guildCode"]
        del kwargs["guildCode"]

        return self._request.call(
            super(PodDealing, self)._get_sc_product_settings("/nzh/biz/addUserAndBusiness", method_type="post"),
            params=kwargs, headers=self._get_headers(), **kwargs)

    def list_user_created_business(self, **kwargs):
        """
        لیست کسب و کارها

        :return: list
        """
        kwargs.setdefault("size", 50)
        kwargs.setdefault("page", 1)
        kwargs["offset"] = calc_offset(kwargs["page"], kwargs["size"])

        self._validate(kwargs, "listUserCreatedBusiness")

        if "guildCode" in kwargs:
            kwargs["guildCode[]"] = kwargs["guildCode"]
            del kwargs["guildCode"]

        if "tags" in kwargs:
            kwargs["tags"] = split_str_to_list(kwargs["tags"])

        if "tagTrees" in kwargs:
            kwargs["tagTrees"] = split_str_to_list(kwargs["tagTrees"])

        return self._request.call(
            super(PodDealing, self)._get_sc_product_settings("/nzh/biz/listUserCreatedBusiness"), params=kwargs,
            headers=self._get_headers(), **kwargs)

    def update_business(self, business_id, business_name, description, guild_code, country, state, city, address,
                        **kwargs):
        """
        ویرایش کسب و کار

        :param int business_id: شناسه کسب و کار
        :param str description: توضیحات
        :param list guild_code: لیستی از کد اصناف
        :param str business_name: نام کسب و کار
        :param str country: کشور محل کسب و کار
        :param str state: استان محل کسب و کار
        :param str city: شهر محل کسب و کار
        :param str address: آدرس محل کسب و کار

        :return: dict
        """

        kwargs["bizId"] = business_id
        kwargs["description"] = description
        kwargs["businessName"] = business_name
        kwargs["country"] = country
        kwargs["state"] = state
        kwargs["city"] = city
        kwargs["address"] = address

        if type(guild_code) == list:
            kwargs["guildCode"] = guild_code
        else:
            kwargs["guildCode"] = [guild_code]

        self._validate(kwargs, "updateBusiness")

        kwargs["guildCode[]"] = kwargs["guildCode"]
        del kwargs["guildCode"]

        return self._request.call(
            super(PodDealing, self)._get_sc_product_settings("/nzh/biz/updateBusiness", method_type="post"),
            params=kwargs, headers=self._get_headers(), **kwargs)

    def get_api_token_for_created_business(self, business_id, **kwargs):
        """
        دریافت توکن کسب و کار ایجاد شده

        :param int business_id: شناسه کسب و کار
        :return: dict
        """
        params = {"businessId": business_id}
        self._validate(params, "getApiTokenForCreatedBusiness")

        return self._request.call(
            super(PodDealing, self)._get_sc_product_settings("/nzh/biz/getApiTokenForCreatedBusiness"),
            params=params, headers=self._get_headers(), **kwargs)

    def rate_business(self, business_id, rate, token=None, **kwargs):
        """
        ثبت امتیاز برای کسب و کار

        :param int business_id: شناسه کسب و کار
        :param int rate: امتیاز بین 0 تا 5
        :param str token: اکسس توکن کاربر - در صورتی که ارسال نشود api token شما قرار میگیرد
        :return: dict
        """
        params = {
            "businessId": business_id,
            "rate": rate
        }

        headers = self._get_headers()
        if token is not None:
            headers["_token_"] = token

        self._validate(params, "rateBusiness")

        return self._request.call(
            super(PodDealing, self)._get_sc_product_settings("/nzh/rateBusiness"), params=params, headers=headers,
            **kwargs)

    def comment_business(self, business_id, comment, token=None, **kwargs):
        """
        ثبت نظر برای کسب و کار

        :param int business_id: شناسه کسب و کار
        :param str comment: نظر
        :param str token: اکسس توکن کاربر - در صورتی که ارسال نشود api token شما قرار میگیرد
        :return: int
        """
        params = {
            "businessId": business_id,
            "text": comment
        }

        headers = self._get_headers()
        if token is not None:
            headers["_token_"] = token

        self._validate(params, "commentBusiness")

        return self._request.call(
            super(PodDealing, self)._get_sc_product_settings("/nzh/commentBusiness"), params=params, headers=headers,
            **kwargs)

    def favorite_business(self, business_id, token=None, **kwargs):
        """
        اضافه کردن کسب و کار به علاقه مندی ها

        :param int business_id: شناسه کسب و کار
        :param str token: اکسس توکن کاربر - در صورتی که ارسال نشود api token شما قرار میگیرد
        :return: boolean
        """
        return self._favorite_business(business_id=business_id, favorite=True, token=token, **kwargs)

    def dis_favorite_business(self, business_id, token=None, **kwargs):
        """
        حذف کسب و کار از علاقمندی ها

        :param int business_id: شناسه کسب و کار
        :param str token: اکسس توکن کاربر - در صورتی که ارسال نشود api token شما قرار میگیرد
        :return: boolean
        """
        return self._favorite_business(business_id=business_id, favorite=False, token=token, **kwargs)

    def _favorite_business(self, business_id, favorite, token=None, **kwargs):
        """
        اضافه کردن و یا حذف کسب و کار از علاقمندی ها

        :param int business_id: شناسه کسب و کار
        :param boolean favorite: آیا از علاقمندی ها حذف بشود یا اضافه بشود؟
        :param str token: اکسس توکن کاربر - در صورتی که ارسال نشود api token شما قرار میگیرد
        :return: boolean
        """
        params = {
            "businessId": business_id,
            "disfavorite": not favorite
        }

        headers = self._get_headers()
        if token is not None:
            headers["_token_"] = token

        self._validate(params, "businessFavorite")

        return self._request.call(
            super(PodDealing, self)._get_sc_product_settings("/nzh/businessFavorite", method_type="post"),
            params=params, headers=headers, **kwargs)

    def user_business_infos(self, business_ids, token=None, **kwargs):
        """
        دریافت امتیاز کاربر نسبت به کسب و کار

        :param list business_ids: لیستی از شناسه های کسب و کار
        :param str token: اکسس توکن کاربر - در صورتی که ارسال نشود api token شما قرار میگیرد
        :return: list
        """

        if type(business_ids) is not list:
            business_ids = [business_ids]

        params = {
            "id": business_ids
        }

        self._validate(params, "userBusinessInfos")

        headers = self._get_headers()
        if token is not None:
            headers["_token_"] = token

        params = {
            "id[]": business_ids
        }

        return self._request.call(
            super(PodDealing, self)._get_sc_product_settings("/nzh/userBusinessInfos"), params=params, headers=headers,
            **kwargs)

    def comment_business_list(self, business_id, token=None, **kwargs):
        """
        لیست نظرات یک کسب و کار

        :param int business_id: شناسه کسب و کار
        :param str token: اکسس توکن کاربر - در صورتی که ارسال نشود api token شما قرار میگیرد
        :return: list
        """
        kwargs["businessId"] = business_id

        if "firstId" not in kwargs and "lastId" not in kwargs and "page" not in kwargs:
            kwargs.setdefault("page", 1)

        kwargs.setdefault("size", 50)

        if "page" in kwargs:
            kwargs["offset"] = calc_offset(kwargs["page"], kwargs["size"])
            del kwargs["page"]

        headers = self._get_headers()
        if token is not None:
            headers["_token_"] = token

        self._validate(kwargs, "commentBusinessList")

        return self._request.call(
            super(PodDealing, self)._get_sc_product_settings("/nzh/commentBusinessList"), params=kwargs,
            headers=headers, **kwargs)

    def confirm_comment(self, comment_id, **kwargs):
        """
        تایید یک نظر

        :param int comment_id: شناسه نظر
        :return: boolean
        """
        params = {
            "commentId": comment_id
        }

        self._validate(params, "confirmComment")

        return self._request.call(
            super(PodDealing, self)._get_sc_product_settings("/nzh/biz/confirmComment"), params=params,
            headers=self._get_headers(), **kwargs)

    def un_confirm_comment(self, comment_id, **kwargs):
        """
        رد یک نظر

        :param int comment_id: شناسه نظر
        :return: boolean
        """
        params = {
            "commentId": comment_id
        }

        self._validate(params, "unconfirmComment")

        return self._request.call(
            super(PodDealing, self)._get_sc_product_settings("/nzh/biz/unconfirmComment"), params=params,
            headers=self._get_headers(), **kwargs)

    def add_dealer_product_permission(self, dealer_biz_id, product_id, **kwargs):
        """
        ثبت مجوز برای فروش محصول توسط یک کسب و کار

        :param int dealer_biz_id: شناسه کسب و کار همکار
        :param int product_id: شناسه محصول
        :return: dict
        """
        params = {
            "dealerBizId": dealer_biz_id,
            "productId": product_id
        }

        self._validate(params, "addDealerProductPermission")

        return self._request.call(
            super(PodDealing, self)._get_sc_product_settings("/nzh/biz/addDealerProductPermission",
                                                             method_type="post"), params=params,
            headers=self._get_headers(), **kwargs)

    def dealer_product_permission_list(self, page=1, size=50, **kwargs):
        """
        لیست مجوزهای اعطا شده به کسب و کارهای واسط دیگر

        :param int page: شماره صفحه
        :param int size: تعداد در هر صفحه
        :return: list
        """
        kwargs["offset"] = calc_offset(page, size)
        kwargs["size"] = size

        self._validate(kwargs, "dealerProductPermissionList")

        return self._request.call(
            super(PodDealing, self)._get_sc_product_settings("/nzh/biz/dealerProductPermissionList"), params=kwargs,
            headers=self._get_headers(), **kwargs)

    def dealing_product_permission_list(self, page=1, size=50, **kwargs):
        """
        مشاهده لیست کسب و کارهایی که شما واسط آنها شده اید و برای آن محصول خاص مجوز صدور فاکتور گرفته اید

        :param int page: شماره صفحه
        :param int size: تعداد در هر صفحه
        :return: list
        """
        kwargs["offset"] = calc_offset(page, size)
        kwargs["size"] = size

        self._validate(kwargs, "dealingProductPermissionList")

        return self._request.call(
            super(PodDealing, self)._get_sc_product_settings("/nzh/biz/dealingProductPermissionList"), params=kwargs,
            headers=self._get_headers(), **kwargs)

    def enable_dealer_product_permission(self, product_id, dealer_biz_id, **kwargs):
        """
        فعال سازی دسترسی محصول در کسب و کار همکار

        :param int product_id: شناسه محصول
        :param int dealer_biz_id: شناسه کسب و کار همکار
        :return: dict
        """
        params = {
            "dealerBizId": dealer_biz_id,
            "productId": product_id
        }

        self._validate(params, "enableDealerProductPermission")

        return self._request.call(
            super(PodDealing, self)._get_sc_product_settings("/nzh/biz/enableDealerProductPermission"), params=params,
            headers=self._get_headers(), **kwargs)

    def disable_dealer_product_permission(self, product_id, dealer_biz_id, **kwargs):
        """
        غیر فعال سازی دسترسی محصول در کسب و کار همکار

        :param int product_id: شناسه محصول
        :param int dealer_biz_id: شناسه کسب و کار همکار
        :return: dict
        """
        params = {
            "dealerBizId": dealer_biz_id,
            "productId": product_id
        }

        self._validate(params, "disableDealerProductPermission")

        return self._request.call(
            super(PodDealing, self)._get_sc_product_settings("/nzh/biz/disableDealerProductPermission"), params=params,
            headers=self._get_headers(), **kwargs)
