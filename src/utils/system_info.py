import json
import subprocess
from functools import lru_cache
from typing import Union
import os
import platform

import psutil
import cpuinfo
from src.models import schemas


def get_ram_info():
    memory = psutil.virtual_memory()

    return schemas.RAMInfo(
        total_space=int(memory.total / 1024 / 1024),
        used_space=int(memory.used / 1024 / 1024),
        free_space=int(memory.free / 1024 / 1024),
        sticks=[],
    )


def get_rom_info():
    disks = []
    output = subprocess.check_output(
        ["lsblk", "-J", "-T", "-oKNAME,TYPE,SIZE,RO,RM,SERIAL,TRAN,MODEL,VENDOR,PATH,FSTYPE,MOUNTPOINT"]
    )
    block_devices = json.loads(output)["blockdevices"]
    for disk in block_devices:
        if disk['type'] == "disk":
            volumes = []
            for volume in disk['children']:
                if not volume['fstype']:
                    continue

                if volume['mountpoint'] in ['/boot/efi', '/boot', "[SWAP]", None]:
                    continue

                if volume['type'] == "part":
                    volumes.append(
                        schemas.ROMVolumeInfo(
                            title=volume['kname'],
                            path=volume['path'],
                            fs_type=volume['fstype'],
                            type=volume['tran'],
                            total_space=volume['size'],
                            ro=volume['ro'],
                            rm=volume['rm'],
                            mount_point=volume['mountpoint'],
                            model=disk['model'],
                            vendor=disk['vendor'],
                            serial=disk['serial'],
                        )
                    )

            disks.append(
                schemas.ROMItemInfo(
                    title=disk['kname'],
                    path=disk['path'],
                    type=disk['tran'],
                    total_space=disk['size'],
                    ro=disk['ro'],
                    rm=disk['rm'],
                    model=disk['model'],
                    vendor=disk['vendor'],
                    serial=disk['serial'],
                    volumes=volumes,
                )
            )
    return schemas.ROMInfo(disks=disks)


@lru_cache(maxsize=128)
def get_cpu_info():
    cpu = cpuinfo.get_cpu_info()
    cpu_freq = psutil.cpu_freq()

    return schemas.CPUInfo(
        model=cpu['brand_raw'],
        manufacturer=cpu['vendor_id_raw'],
        architecture=cpu['arch'],
        bits=cpu['bits'],
        max_freq=cpu_freq.max,
        base_freq=cpu['hz_advertised'][0] / 1000 / 1000,
        min_freq=cpu_freq.min,
        physical_cores=psutil.cpu_count(logical=False),
        logical_cores=psutil.cpu_count(logical=True),
    )


def get_os_info():
    data = platform.uname()
    return schemas.OSInfo(
        system=data.system,
        node=data.node,
        release=data.release,
        version=data.version,
        machine=data.machine,
    )
