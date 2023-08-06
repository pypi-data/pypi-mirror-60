import os
import asyncio
import logging
import traceback

from apistar import ASyncApp, exceptions
from apistar.http import Response, JSONResponse
from apistar.server.components import ReturnValue
from apistar.server.asgi import ASGIScope, ASGISend

from apistellar.bases.entities import settings
from apistellar.bases.websocket import WebSocketApp
from apistellar.document import ShowLogPainter, AppLogPainter
from apistellar.bases.components import Component, ComposeTypeComponent
from apistellar.bases.hooks import WebContextHook, ErrorHook, \
    AccessLogHook, SessionHook, Hook
from apistellar.helper import TypeEncoder, find_children, enhance_response

__all__ = ["Application"]
enhance_response(Response)
# 可以序列化Type子类
JSONResponse.options["default"] = TypeEncoder().default

del JSONResponse.charset


RESP_BUFFER_SIZE = 1024000


class FixedAsyncApp(ASyncApp):

    def exception_handler(self, exc: Exception) -> Response:
        """
        如果是HTTP的异常，不会走on_error逻辑，否则，走on_error逻辑
        :param exc:
        :return:
        """
        if isinstance(exc, exceptions.HTTPException):
            payload = {
                "type": "http",
                "code": exc.status_code,
                "errcode": exc.status_code,
                "message": exc.detail,
            }
            if self.debug:
                payload["detail"] = "".join(traceback.format_exc())
            return JSONResponse(payload, exc.status_code, exc.get_headers())
        raise exc

    def error_handler(self, return_value: ReturnValue, resp: Response) -> Response:
        if resp is not None:
            return resp
        if isinstance(return_value, Response):
            return return_value
        return super().error_handler()

    async def read(self, response):
        coroutine = response.content.read(RESP_BUFFER_SIZE)
        if asyncio.iscoroutine(coroutine) or asyncio.isfuture(coroutine):
            return await coroutine
        else:
            return coroutine

    async def finalize_asgi(self,
                            response: Response,
                            send: ASGISend,
                            scope: ASGIScope):
        if response.exc_info is not None:
            if self.debug or scope.get('raise_exceptions', False):
                exc_info = response.exc_info
                raise exc_info[0].with_traceback(exc_info[1], exc_info[2])

        await send({
            'type': 'http.response.start',
            'status': response.status_code,
            'headers': [
                [key.encode(), value.encode()]
                for key, value in response.headers
            ]
        })
        if hasattr(response.content, "read"):
            body = await self.read(response)
            while body:
                await send({
                    'type': 'http.response.body',
                    'body': body,
                    "more_body": True,
                })
                body = await self.read(response)
        else:
            body = response.content
        await send({
            'type': 'http.response.body',
            'body': body
        })

    def __call__(self, scope):
        if scope["type"] != "websocket":
            return super(FixedAsyncApp, self).__call__(scope)
        else:
            return WebSocketApp(scope, self)


def application(app_name,
                packages=None,
                static_url='/static/',
                settings_path="settings",
                debug=True,
                current_dir="."):
    """
       可以动态发现当前项目根目录下所有controller中的handler
    """
    logger = logging.getLogger(app_name)
    os.chdir(current_dir)
    with AppLogPainter(logger.debug, current_dir, settings_path).paint() as routes:
        components = find_children(Component)
        # ComposeTypeComponent是用来兜底的，所以要放到最后
        components.append(ComposeTypeComponent())
        custom_hooks = sorted(find_children(Hook), key=lambda x: x.order)
        hooks = [WebContextHook(), SessionHook(), ErrorHook()] + custom_hooks
        app = FixedAsyncApp(
            routes,
            template_dir=settings.get("TEMPLATE_DIR"),
            static_dir=settings.get("STATIC_DIR"),
            packages=packages,
            schema_url=None,
            docs_url=None,
            static_url=static_url,
            components=components,
            event_hooks=hooks)
        app.debug = debug
        return app


Application = application


def show_routes():
    formatter = "{:<40} {:<7} {:<40} {:<}"

    def show_format(method, parttern, name, ca_name):
        return formatter.format(name, method, parttern, ca_name)

    with ShowLogPainter(show_format).paint() as routes:
        if routes:
            print(formatter.format(
                "Name", "Method", "URI Pattern", "Controller#Action"))
