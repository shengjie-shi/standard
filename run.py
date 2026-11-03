# -*- coding: utf-8 -*-

def remove_zipfiles(root_path):
    """Remove downloaded zip files"""
    import os
    from os.path import join as opj
    zipfile_list = [f for f in os.listdir(root_path) if f.endswith(".zip")]
    for zipfile in zipfile_list:
        os.remove(opj(root_path, zipfile))


def run_init(args):
    from epointml.utils import commonUtil, elog

    commonUtil.set_args(args)
    commonUtil.setRootPath("./")

    logger = elog()
    logger.info("[*] Initialization stage...")
    logger.info("[*] Installing required packages...")
    commonUtil.installpackage(args["whlsource"], no_dependencies=True)

    logger.info("[*] Finish initializing")

    return "OK"


def run_deploy(args):
    import uvicorn
    from config.defaults import get_args

    args = get_args(args)

    import os
    import shutil
    from os.path import join as opj
    from fastapi import FastAPI, APIRouter
    from tools.common import get_host_ip
    from epointml.utils import commonUtil, elog
    from APIManager.RestApi import ApiManager

    commonUtil.setRootPath("./")
    logger = elog()
    commonUtil.set_args(args)
    app = FastAPI()
    router = APIRouter()
    ip = get_host_ip()

    # download_model_dir = "models_infer"
    # args["encode_model_dir"] = opj(download_model_dir, args["encode_model_folder"])
    #
    # if not os.path.exists(download_model_dir):
    #     os.makedirs(download_model_dir)
    #     commonUtil.downloadModel(logger,
    #                              url=args["encode_model_url"],
    #                              zippath=opj(download_model_dir, "encode_model.zip"),
    #                              tarpath=args['encode_model_dir'])
    #     logger.info("[*] Encode model downloaded")
    #
    #     remove_zipfiles(root_path=download_model_dir)
    # else:
    #     logger.info("[*] Models already prepared, please make sure they are located in right folders...")

    system = ...

    logger.info("[*] System Ready...")

    rest_api = ApiManager(logger, system=system)

    # 反射调用定义服务接口
    router.add_api_route(f"/{args.serviceName}/check", getattr(rest_api, "api_check"), methods=['GET'])
    router.add_api_route(f"/{args.serviceName}/version", getattr(rest_api, "api_version"), methods=["GET"])
    router.add_api_route(f"/{args.serviceName}/predict", getattr(rest_api, "api_predict"), methods=['POST'])

    app.include_router(router)

    logger.info("[*] Start Service")
    logger.info(f"[*] http://{ip}:{args['port']}/{args['serviceName']}/predict")
    commonUtil.sendRestReadySignal()

    uvicorn.run(app, host=args.host, port=args.port, log_level="debug")

    return "OK"


if __name__ == "__main__":

    from epointml.utils import commonUtil
    commonUtil.setRootPath("./")

    args = commonUtil.load_step_param("deploy")
    run_deploy(args)


