# coding=utf-8
from os import path

from pod_base import PodBase, calc_offset, NotFoundException
from .exceptions import PodExportException


class PodExport(PodBase):
    EXPORT_SERVICE_STATUS_CREATED = "EXPORT_SERVICE_STATUS_CREATED"
    EXPORT_SERVICE_STATUS_RUNNING = "EXPORT_SERVICE_STATUS_RUNNING"
    EXPORT_SERVICE_STATUS_SUCCESSFUL = "EXPORT_SERVICE_STATUS_SUCCESSFUL"
    EXPORT_SERVICE_STATUS_FAILED = "EXPORT_SERVICE_STATUS_FAILED"

    def __init__(self, api_token, token_issuer="1", server_type="sandbox", config_path=None,
                 sc_api_key="", sc_voucher_hash=None):
        here = path.abspath(path.dirname(__file__))
        self._services_file_path = path.join(here, "services.ini")
        super(PodExport, self).__init__(api_token, token_issuer, server_type, config_path, sc_api_key, sc_voucher_hash,
                                        path.join(here, "json_schema.json"))

    def get_export_list(self, page=1, size=20, **kwargs):
        """
        دریافت لیست درخواست های دریافت گزارشات به صورت فایل

        :param int page: شماره صفحه
        :param int size: تعداد در هر صفحه
        :return: list
        """
        params = kwargs
        params["offset"] = calc_offset(page, size)
        params["size"] = size

        self._validate(params, "getExportList")

        return self._request.call(sc_product_id=super(PodExport, self).
                                  _get_sc_product_id("/nzh/biz/getExportList"), params=params,
                                  headers=self._get_headers(), **kwargs)

    def get_export(self, request_id, **kwargs):
        """
        دریافت جزئیات یک گزارش

        :param int request_id: شناسه درخواست
        :return: dict
        """
        request = self.get_export_list(id=request_id, **kwargs)
        if len(request):
            return request[0]

        raise NotFoundException("درخواست گزارشی با شناسه {} یافت نشد.".format(request_id))

    def get_download_link(self, request_id, **kwargs):
        """
        تولید لینک دانلود فایل گزارش

        :param int request_id: شناسه درخواست
        :return: str
        """
        request = self.get_export(request_id=request_id, **kwargs)
        if request["statusCode"] == PodExport.EXPORT_SERVICE_STATUS_SUCCESSFUL:
            result_file = request["resultFile"]
            return "{}/nzh/file/?fileId={}&hashCode={}".format(
                self.config.get("file_server_address", self._server_type), result_file["id"], result_file["hashCode"])

        raise PodExportException(message="هنوز فایل برای دانلود آماده نشده است")
