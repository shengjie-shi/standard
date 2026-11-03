# -*- coding: utf-8 -*-
"""
Description:

@Author: ssjie

Created on: 2024/6/28
"""
import os
import subprocess


def get_host_ip():
    """
    查询本机ip地址
    """
    import socket

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
    finally:
        s.close()

    return ip


def check_port_in_use(host, port):
    import socket
    print(f'Checking if host & port is available :: {host}:{port}')
    host = host.replace('https://', '').replace('http://', '')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, int(port))) == 0


def get_free_port(port, debug=False):
    # check port is busy
    if not debug:
        original_port = int(port)
        # try up to 1000 new ports
        while check_port_in_use('localhost', port):
            old_port = port
            port = int(port) + 1
            if port - original_port >= 1000:
                raise ConnectionError(
                    '\n*** WARNING! ***\n Could not find an available port\n'
                    + ' to launch label studio. \n Last tested port was '
                    + str(port)
                    + '\n****************\n'
                )
            print(
                '\n*** WARNING! ***\n* Port '
                + str(old_port)
                + ' is in use.\n'
                + '* Trying to start at '
                + str(port)
                + '\n****************\n'
            )
    return port


def str2bool(v):
    if isinstance(v, bool) or isinstance(v, int):
        return bool(v)
    return v.lower() in ("true", "t", "1")


def gpu_strategy(use_gpu=True, cuda_device="-1"):
    # -------GPU auto select helpers-------
    def get_gpu_utilization():
        """Returns a list of GPU utilization as a percentage"""
        output = subprocess.check_output(
            ['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'],
            encoding='utf-8')
        gpu_utilization = [int(x) for x in output.strip().split('\n')]
        return gpu_utilization

    def get_gpu_memory():
        """Returns a list of available GPU memory in MB"""
        output = subprocess.check_output(
            ['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
            encoding='utf-8')
        memory_available = [int(x) for x in output.strip().split('\n')]
        return memory_available

    def select_gpu(mode="-1"):
        if mode == "-2":
            """Returns the index of the GPU with the lowest utilization"""
            gpu_utilization = get_gpu_utilization()
            index, _ = min(enumerate(gpu_utilization), key=lambda x: x[1])
            return index
        if mode == "-1":
            """Returns the index of the GPU with the most available memory"""
            memory_available = get_gpu_memory()
            index, _ = max(enumerate(memory_available), key=lambda x: x[1])
            return index
            # -------GPU auto select helpers ends here-------

    # set args
    if isinstance(cuda_device, str):
        # args["cuda_device"] could potentially be multiple GPUs, like "0,1"
        # split it and store them in a list
        cuda_device = cuda_device.replace("，", ",").split(",")
    if use_gpu:
        # check if args["cuda_device"] is valid.
        # args["cuda_device"] cannot be bigger than device_count,
        # or smaller than -2. If it is, set it to -1
        try:
            output = subprocess.check_output(['nvidia-smi', '--list-gpus'], encoding='utf-8')
        except FileNotFoundError:
            print("没有找到nvidia-smi，请检查环境中是否有GPU，或是否正确安装了nvidia驱动")
            # raise FileNotFoundError("nvidia-smi is not found, please check if nvidia-smi is installed.")
            # will use cpu if nvidia-smi is not found.
            cuda_device = 'cpu'
            os.environ["CUDA_VISIBLE_DEVICES"] = 'cpu'
            print(f"[*] Going to use device: {cuda_device}")
            return os.environ["CUDA_VISIBLE_DEVICES"]

        device_count = len(output.splitlines())
        # check if args["cuda_device"] is valid.
        for gpu_index in cuda_device:
            if int(gpu_index) > (device_count - 1) or int(gpu_index) < -2:
                cuda_device = ["-1"]
                break

        if len(cuda_device) > 1:
            # select GPUs by user specified GPU indices.
            gpu_index = ','.join(cuda_device)
            os.environ["CUDA_VISIBLE_DEVICES"] = gpu_index
            print(f"[*] Going to use device cuda: {gpu_index}")
        else:
            # select GPU according to GPU resources.
            if int(cuda_device[0]) < 0:  # use strategy to select gpu
                gpu_index = str(select_gpu(cuda_device[0]))
                cuda_device = gpu_index
                os.environ["CUDA_VISIBLE_DEVICES"] = gpu_index
            else:  # use the user specified GPU.
                os.environ["CUDA_VISIBLE_DEVICES"] = cuda_device[0]
            print(f"[*] Going to use device cuda:{cuda_device[0]}")
    else:
        cuda_device = 'cpu'
        # set os.environ["CUDA_VISIBLE_DEVICES"]
        os.environ["CUDA_VISIBLE_DEVICES"] = 'cpu'
        print(f"[*] Going to use device: {cuda_device}")
    return os.environ["CUDA_VISIBLE_DEVICES"]


def get_gpu_mem_info(gpu_id=0, unit="mb"):

    unit = unit.lower()
    assert unit in ["gb", "mb"]

    import pynvml
    pynvml.nvmlInit()

    if gpu_id < 0 or gpu_id >= pynvml.nvmlDeviceGetCount():
        raise f"gpu id {gpu_id} out of range!"

    handler = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
    memory_info = pynvml.nvmlDeviceGetMemoryInfo(handler)
    utilization = pynvml.nvmlDeviceGetUtilizationRates(handler)

    total = memory_info.total
    used = memory_info.used
    free = memory_info.free

    if unit == "mb":
        total, used, free = list(map(lambda x: round(x / 1024 / 1024, 2), [total, used, free]))
    else:
        total, used, free = list(map(lambda x: round(x / 1024 / 1024 / 1024, 2), [total, used, free]))

    return total, used, free


def get_available_gpus(gpu_memory_thres=0.7, unit="mb"):

    import pynvml
    pynvml.nvmlInit()

    available_gpus = []

    for gpu_id in range(pynvml.nvmlDeviceGetCount()):
        total, used, free = get_gpu_mem_info(gpu_id, unit=unit)
        if free / total >= gpu_memory_thres:
            available_gpus.append(
                {
                    "gpu_id": gpu_id,
                    "free": free,
                    "used": used,
                    "total": total
                }
            )
    return available_gpus


def get_dir_size(path, unit="mb", ignore_dir=False):
    unit = unit.lower()
    assert unit.lower() in ["gb", "mb"]

    if os.path.isfile(path):
        total = os.path.getsize(path)
    else:
        total = 0
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    if not ignore_dir:
                        total += get_dir_size(entry.path)

    if unit == "mb":
        total = round(total / 1024 / 1024, 2)
    else:
        total = round(total / 1024 / 1024 / 1024, 2)

    return total


def estimate_memory(model_path, dtype="bf16", unit="mb", redundancy=0.2):
    # TODO: 研究下accelerate estimate-memory能否获取模型的显存占用数据
    model_file_size = get_dir_size(model_path, unit=unit, ignore_dir=True)

    estimated_size = (1 + redundancy) * model_file_size

    if dtype == "float32":
        estimated_size *= 2
    elif dtype == "int8":
        estimated_size /= 2
    elif dtype == "int4":
        estimated_size /= 4

    return estimated_size


if __name__ == "__main__":

    use_gpu = True
    cuda_devices = "-1"

    # cuda_visible_devices = gpu_strategy(use_gpu, cuda_devices)
    #
    # print(cuda_visible_devices)

    print(get_available_gpus(0.3))


