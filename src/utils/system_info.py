import asyncio
import json
import logging
import re
import subprocess
from functools import lru_cache
from typing import Union, Any, List, Optional
from socket import AddressFamily
import fcntl
import socket
import struct
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


def get_os_info() -> schemas.OSInfo:
    data = platform.uname()
    return schemas.OSInfo(
        system=data.system,
        node=data.node,
        release=data.release,
        version=data.version,
        machine=data.machine,
    )


def get_mac_address(interface: str) -> Optional[str]:
    """
    Get the MAC address of a network interface
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', bytes(interface, 'utf-8')[:15]))
    return ':'.join('%02x' % b for b in info[18:24])


async def async_ping(host: str, interface: str, timeout: int) -> schemas.LANNetworkItemInfo:
    """
    Ping host using interface

    async vers
    """
    proc = await asyncio.create_subprocess_shell(
        f"ping -I {interface} -c 1 -W {timeout} {host}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    if stdout:
        result = re.findall(r"(\d+)% packet loss", stdout.decode())

        if not result:
            schemas.LANNetworkItemInfo(
                interface=interface,
                has_global_network=False,
            )

        loss_perc = int(result[0])
        return schemas.LANNetworkItemInfo(
            interface=interface,
            has_global_network=loss_perc == 0,
        )

    if stderr:
        logging.warning("Error ping host: %s", stderr.decode())
        schemas.LANNetworkItemInfo(
            interface=interface,
            has_global_network=False,
        )


async def get_network_info() -> schemas.LANNetworkInfo:
    interface_names = []
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        if interface_name == 'lo':
            continue
        interface_names.append(interface_name)

    result = await asyncio.gather(
        *[async_ping('google.com', interface, 1) for interface in interface_names],
    )
    return schemas.LANNetworkInfo(interfaces=result)


def get_lan_info() -> schemas.LANInfo:
    interfaces = []
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        if interface_name == 'lo':
            continue

        interfaces.append(
            schemas.LANItemInfo(
                title=interface_name,
                is_up=psutil.net_if_stats()[interface_name].isup,
                speed=psutil.net_if_stats()[interface_name].speed,
                mac=get_mac_address(interface_name),
                addresses=[schemas.LANAddressInfo(
                    address=address.address,
                    netmask=address.netmask,
                    broadcast=address.broadcast,
                    family=address.family.name,
                ) for address in interface_addresses],
            )
        )
    return schemas.LANInfo(interfaces=interfaces)


def get_cpu_stat() -> schemas.CPUStat:
    count_of_cores = psutil.cpu_count(logical=False)
    cores_percent: list[float] = psutil.cpu_percent(percpu=True)
    cores_freq: list[Any] = psutil.cpu_freq(percpu=True)
    cores_temp: list[Any] = psutil.sensors_temperatures().get('coretemp')
    cores = []
    for i in range(count_of_cores):
        cores.append(
            schemas.CPUStatCore(
                percent=cores_percent[i],
                freq=cores_freq[i].current,
                temperature=None if cores_temp is None else cores_temp[i].current,
            )
        )

    return schemas.CPUStat(
        percent=psutil.cpu_percent(),
        freq=psutil.cpu_freq().current,
        temperature=None if cores_temp is None else cores_temp[0].current,
        cores=cores,
    )


def get_ram_stat() -> schemas.RAMStat:
    memory = psutil.virtual_memory()
    return schemas.RAMStat(
        total_space=int(memory.total / 1024 / 1024),
        used_space=int(memory.used / 1024 / 1024),
        free_space=int(memory.free / 1024 / 1024),
        percent=memory.percent,
    )


def get_rom_stat() -> schemas.ROMStat:
    volumes = []
    disks = get_rom_info().disks
    if not disks:
        return schemas.ROMStat(disks=[])
    for disk in disks:
        for volume in disk.volumes:
            total, used, free, percent = psutil.disk_usage(volume.path)
            volumes.append(
                schemas.ROMStatVolume(
                    title=volume.title,
                    path=volume.path,
                    fs_type=volume.fs_type,
                    type=volume.type,
                    total_space=total,
                    used_space=used,
                    free_space=free,
                    percent=percent,
                )
            )
    return schemas.ROMStat(volumes=volumes)


def get_lan_stat() -> schemas.LANStat:
    interfaces = []
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        if interface_name == 'lo':
            continue

        interfaces.append(
            schemas.LANStatInterface(
                title=interface_name,
                bytes_sent=psutil.net_io_counters(pernic=True)[interface_name].bytes_sent,
                bytes_recv=psutil.net_io_counters(pernic=True)[interface_name].bytes_recv,
            )
        )
    return schemas.LANStat(interfaces=interfaces)
