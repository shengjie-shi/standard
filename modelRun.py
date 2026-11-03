from run import run_init, run_deploy


def exe_init(args):
    return run_init(args)


def exe_deploy(args):
    return run_deploy(args)


if __name__ == "__main__":
    import os
    from epointml.utils import commonUtil
    commonUtil.setRootPath(os.path.split(os.path.realpath(__file__))[0])
    args = commonUtil.load_step_param("deploy")
    exe_deploy(args)
