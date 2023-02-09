from typing import Optional

from pydantic import BaseModel


class CPUInfo(BaseModel):
    model: Optional[str]
    architecture: Optional[str]
    bits: Optional[int]
    manufacturer: Optional[str]
    max_freq: Optional[float]
    base_freq: Optional[float]
    min_freq: Optional[float]
    physical_cores: Optional[int]
    logical_cores: Optional[int]


class RAMItemInfo(BaseModel):
    total_space: Optional[int]
    form_factor: Optional[str]
    type: Optional[str]
    manufacturer: Optional[str]
    speed: Optional[float]
    config_speed: Optional[float]
    serial_number: Optional[str]


class RAMInfo(BaseModel):
    total_space: Optional[int]
    used_space: Optional[int]
    free_space: Optional[int]
    sticks: Optional[list[RAMItemInfo]]


class ROMVolumeInfo(BaseModel):
    title: Optional[str]
    path: Optional[str]
    fs_type: Optional[str]
    type: Optional[str]
    total_space: Optional[str]
    ro: Optional[bool]
    rm: Optional[bool]
    mount_point: Optional[str]
    model: Optional[str]
    vendor: Optional[str]
    serial: Optional[str]


class ROMItemInfo(BaseModel):
    title: Optional[str]
    path: Optional[str]
    type: Optional[str]
    total_space: Optional[str]
    ro: Optional[bool]
    rm: Optional[bool]
    model: Optional[str]
    vendor: Optional[str]
    serial: Optional[str]
    volumes: Optional[list[ROMVolumeInfo]]


class ROMInfo(BaseModel):
    disks: list[ROMItemInfo]


class LANAddressInfo(BaseModel):
    address: Optional[str]
    netmask: Optional[str]
    broadcast: Optional[str]
    family: Optional[str]


class LANNetworkItemInfo(BaseModel):
    interface: Optional[str]
    has_global_network: Optional[bool]


class LANNetworkInfo(BaseModel):
    interfaces: Optional[list[LANNetworkItemInfo]]


class LANItemInfo(BaseModel):
    title: Optional[str]
    speed: Optional[int]
    mac: Optional[str]
    is_up: Optional[bool]
    addresses: Optional[list[LANAddressInfo]]


class LANInfo(BaseModel):
    interfaces: Optional[list[LANItemInfo]]


class OSInfo(BaseModel):
    system: Optional[str]
    node: Optional[str]
    release: Optional[str]
    version: Optional[str]
    machine: Optional[str]


class SystemInfo(BaseModel):
    cpu: CPUInfo
    ram: RAMInfo
    rom: ROMInfo
    lan: LANInfo
    os: OSInfo


# ------------ stats ------------


class CPUStatCore(BaseModel):
    percent: Optional[float]
    freq: Optional[float]
    temperature: Optional[float]


class CPUStat(BaseModel):
    percent: Optional[float]
    freq: Optional[float]
    temperature: Optional[float]
    cores: Optional[list[CPUStatCore]]


class RAMStat(BaseModel):
    total_space: Optional[int]
    used_space: Optional[int]
    free_space: Optional[int]
    swap_total_space: Optional[int]
    swap_used_space: Optional[int]
    swap_free_space: Optional[int]


class ROMStatVolume(BaseModel):
    title: Optional[str]
    path: Optional[str]
    fs_type: Optional[str]
    type: Optional[str]
    total_space: Optional[int]
    used_space: Optional[int]
    free_space: Optional[int]
    percent: Optional[float]


class ROMStat(BaseModel):
    volumes: Optional[list[ROMStatVolume]]


class LANStatInterface(BaseModel):
    title: Optional[str]
    ip: Optional[str]
    bytes_sent: Optional[int]
    bytes_recv: Optional[int]
    current_speed_up: Optional[float]
    current_speed_down: Optional[float]


class LANStat(BaseModel):
    adapters: Optional[list[LANStatInterface]]


class SystemStat(BaseModel):
    cpu: CPUStat
    ram: RAMStat
    rom: ROMStat
    lan: LANStat
