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
    os: OSInfo
