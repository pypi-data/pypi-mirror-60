# coding=utf-8
from __future__ import unicode_literals
from os import path
from pod_base import PodBase, calc_offset


class PodCommon(PodBase):

    def __init__(self, api_token, token_issuer="1", server_type="sandbox", config_path=None,
                 sc_api_key="", sc_voucher_hash=None):
        here = path.abspath(path.dirname(__file__))
        self._services_file_path = path.join(here, "services.json")
        super(PodCommon, self).__init__(api_token, token_issuer, server_type, config_path, sc_api_key, sc_voucher_hash,
                                        path.join(here, "json_schema.json"))

    def get_ott(self, **kwargs):
        """
        دریافت آخرین توکن یکبار مصرف

        :return
        """
        self._request.call(super(PodCommon, self)._get_sc_product_settings("/nzh/ott"), headers=self._get_headers()
                           , **kwargs)
        return str(self._request.last_ott)

    def currency_list(self, **kwargs):
        """
        دریافت لیست ارزها

        :return: list
        """
        return self._request.call(super(PodCommon, self)._get_sc_product_settings("/nzh/currencyList"),
                                  headers=self._get_headers(), **kwargs)

    def guild_list(self, name=None, page=1, size=50, **kwargs):
        """
        لیست اصناف

        :param str name: جستجو در نام اصناف
        :param int page: شماره صفحه
        :param int size: تعداد آیتم در هر صفحه
        :return: list
        """
        params = {
            "offset": calc_offset(page, size),
            "size": size
        }
        if name is not None:
            params["name"] = name

        return self._request.call(super(PodCommon, self)._get_sc_product_settings("/nzh/guildList"), params=params,
                                  headers=self._get_headers(), **kwargs)

    def add_tag_tree_category(self, name, desc="", **kwargs):
        """
        ایجاد دسته بندی برچسب درختی

        :param str name: نام دسته بندی
        :param str desc: توضحیات
        :return
        """
        params = {}
        if name.__len__():
            params["name"] = name

        if desc.__len__():
            params["desc"] = desc

        self._validate(params, "addTagTreeCategory")

        return self._request.call(super(PodCommon, self)._get_sc_product_settings("/nzh/biz/addTagTreeCategory",
                                                                                  "post"),
                                  params=params, headers=self._get_headers(), **kwargs)

    def get_tag_tree_category_list(self, params=None, page=1, size=50, **kwargs):
        """
        لیست دسته بندی های برچسب درختی

        :param dict params: فیلترها
        :param int page: شماره صفحه
        :param int size: تعداد آیتم در هر صفحه
        :return: list
        """
        if params is None:
            params = {}

        params.update({
            "offset": calc_offset(page, size),
            "size": size
        })

        self._validate(params, "getTagTreeCategoryList")

        return self._request.call(super(PodCommon, self)._get_sc_product_settings("/nzh/biz/getTagTreeCategoryList"),
                                  params=params, headers=self._get_headers(), **kwargs)

    def update_tag_tree_category(self, category_id, name, desc, enable=True, **kwargs):
        """
        ویرایش اطلاعات دسته بندی برچسب درختی

        :param int category_id: شناسه دسته بندی
        :param str name: نام جدید دسته بندی
        :param str desc: توضیحات جدید دسته بندی
        :param bool enable: وضعیت فعال یا غیرفعال بودن دسته بندی
        :return
        """
        params = {
            "id": category_id,
            "name": name,
            "desc": desc,
            "enable": enable
        }

        self._validate(params, "updateTagTreeCategory")

        return self._request.call(super(PodCommon, self)._get_sc_product_settings("/nzh/biz/updateTagTreeCategory",
                                                                                  "post"),
                                  params=params, headers=self._get_headers(), **kwargs)

    def add_tag_tree(self, name, code, category_id, parent_id=0, **kwargs):
        """
        اضافه کردن تگ به درخت تگ ها

        :param str name: نام تگ
        :param str code: کد تگ
        :param int category_id: شناسه دسته بندی درخت تگ
        :param int parent_id: شناسه تگ پدر
        :return
        """

        params = {
            "name": name,
            "categoryId": category_id,
            "code": code
        }

        if parent_id:
            params["parentId"] = parent_id

        self._validate(params, "addTagTree")

        return self._request.call(super(PodCommon, self)._get_sc_product_settings("/nzh/biz/addTagTree", "post"),
                                  params=params, headers=self._get_headers(), **kwargs)

    def _get_tag_tree_list(self, params, **kwargs):
        self._validate(params, "getTagTreeList")

        return self._request.call(super(PodCommon, self)._get_sc_product_settings("/nzh/biz/getTagTreeList"),
                                  params=params, headers=self._get_headers(), **kwargs)

    def get_tag_tree_list(self, category_id, level_count=3, level=0, parent_id=0, **kwargs):
        """
        لیست برچسب درختی

        :param int category_id: شناسه دسته بندی برچسب درختی
        :param int level_count: تعداد سطح ها
        :param int level: سطح شروع
        :param int parent_id: شناسه والد
        :return: list
        """

        params = {
            "categoryId": category_id,
            "levelCount": level_count,
            "level": level
        }

        if parent_id:
            params["parentId"] = parent_id
            del params["level"]

        return self._get_tag_tree_list(params)

        return self._get_tag_tree_list(params, **kwargs)

    def get_tag_tree(self, tag_tree_id, **kwargs):
        """
        دریافت جزئیات یک برچسب درختی

        :param int tag_tree_id: شناسه برچسب درختی
        :return
        """
        params = {
            "id": tag_tree_id
        }

        result = self._get_tag_tree_list(params, **kwargs)
        if len(result):
            return result[0]

        return {}

    def update_tag_tree(self, tag_tree_id, name, parent_id=0, enable=True, **kwargs):
        """
        ویرایش برچسب درختی

        :param int tag_tree_id: شناسه برچسب درختی
        :param str name: نام برچسب درختی
        :param int parent_id: شناسه والد برچسب درختی
        :param bool enable: فعال یا غیرفعال بودن برچسب
        :return
        """
        params = {
            "id": tag_tree_id,
            "name": name,
            "enable": enable
        }

        if parent_id:
            params["parentId"] = parent_id

        self._validate(params, "updateTagTree")

        return self._request.call(super(PodCommon, self)._get_sc_product_settings("/nzh/biz/updateTagTree", "post"),
                                  params=params, headers=self._get_headers(), **kwargs)
