import asyncio

from aiohttp import web
from server import PromptServer

from .nodes import (
    NODE_CLASS_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS,
    open_output_directory,
    select_output_directory,
)


def _is_local_request(request):
    return request.remote in {None, "127.0.0.1", "::1"}


prompt_server = getattr(PromptServer, "instance", None)

if prompt_server:
    routes = prompt_server.routes

    @routes.post("/qwen3_asr_hf/select_output_dir")
    async def select_output_dir(request):
        if not _is_local_request(request):
            raise web.HTTPForbidden(text="仅允许本机选择文件夹。")

        data = await request.json()
        selected = await asyncio.to_thread(
            select_output_directory,
            str(data.get("path", "")),
        )
        return web.json_response({"path": selected})

    @routes.post("/qwen3_asr_hf/select_input_dir")
    async def select_input_dir(request):
        if not _is_local_request(request):
            raise web.HTTPForbidden(text="仅允许本机选择文件夹。")

        data = await request.json()
        selected = await asyncio.to_thread(
            select_output_directory,
            str(data.get("path", "")),
            "选择需要批量识别的音频文件夹",
        )
        return web.json_response({"path": selected})

    @routes.post("/qwen3_asr_hf/open_output_dir")
    async def open_output_dir(request):
        if not _is_local_request(request):
            raise web.HTTPForbidden(text="仅允许本机打开文件夹。")

        data = await request.json()
        opened = await asyncio.to_thread(
            open_output_directory,
            str(data.get("path", "")),
        )
        return web.json_response({"path": opened})


WEB_DIRECTORY = "./web"

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY",
]
