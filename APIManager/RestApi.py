"""
Description: 

@Author: ssjie

Created on: 2021/8/9
"""
import time
import json
import traceback
import datetime
from fastapi import Request
from fastapi.responses import JSONResponse, Response, StreamingResponse, PlainTextResponse
from APIManager.Response import success, fail
from APIManager.protocol import SystemRequest


class ApiManager(object):

    def __init__(self, logger, system):
        """
        System is one of the application, e.g. OCRGeneral, OCRCert...
        """
        self.logger = logger
        self.system = system

    @staticmethod
    async def api_check():
        return PlainTextResponse("OK")

    @staticmethod
    async def show_version():
        from __init__ import __version__
        ver = {"version": __version__}
        return JSONResponse(content=ver)

    @staticmethod
    async def api_version():
        from __init__ import __version__
        return PlainTextResponse(__version__)

    async def api_predict(self, request: SystemRequest, raw_request: Request):
        """take notes
        """
        try:
            request_ip = raw_request.headers['X-Forwarded-For']
        except KeyError:
            request_ip = raw_request.client.host

        try:

            # TODO: request

            request_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            rst = await self.system(request)

            if rst is None:
                return json.dumps(fail("Nothing detected"))

            ret = success(rst.model_dump(), request_ip=request_ip, request_time=request_time)

        except Exception as e:
            ret = fail(str(e))
            self.logger.error('traceback.format_exc():\n%s' % traceback.format_exc())

        return JSONResponse(ret)












