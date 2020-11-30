"""
Device info reader class implementation.
"""

from pathlib import Path

class RecoveryImageInfoReader:
    """
    This class is responsible for reading device information from ramdisk
    """
    # pylint: disable=too-many-instance-attributes, too-few-public-methods

    def __init__(self, aik_ramdisk_path: Path, aik_images_path: Path):
        """
        Device info reader class constructor
        :param aik_ramdisk_path: Extracted ramdisk path as a Path object
        :param aik_images_path: Extracted images path as Path object
        """
        self.aik_ramdisk_path = aik_ramdisk_path
        self.aik_images_path = aik_images_path
        self.aik_images_path_base = str(aik_images_path / "recovery.img-")
        self.has_kernel = self.get_extracted_info("zImage").is_file()
        self.has_dt_image = self.get_extracted_info("dt").is_file()
        self.has_dtb_image = self.get_extracted_info("dtb").is_file()
        self.has_dtbo_image = self.get_extracted_info("dtbo").is_file()
        self.base_address = self.read_recovery_file(self.get_extracted_info("base"))
        self.board_name = self.read_recovery_file(self.get_extracted_info("board"))
        self.cmdline = self.read_recovery_file(self.get_extracted_info("cmdline"))
        header_version = self.get_extracted_info("header_version")
        self.header_version = self.read_recovery_file(header_version) if header_version.exists() else "0"
        self.recovery_size = self.read_recovery_file(self.get_extracted_info("origsize"))
        self.pagesize = self.read_recovery_file(self.get_extracted_info("pagesize"))
        self.ramdisk_compression = self.read_recovery_file(self.get_extracted_info("ramdiskcomp"))
        self.ramdisk_offset = self.read_recovery_file(self.get_extracted_info("ramdisk_offset"))
        self.tags_offset = self.read_recovery_file(self.get_extracted_info("tags_offset"))
        self.kernel_name = ''

    @staticmethod
    def read_recovery_file(file: Path) -> str:
        """
        Read file contents
        :param file: file as a Path object
        :return: string of the first line of the file contents
        """
        return file.read_text().splitlines()[0]

    def get_extracted_info(self, file: str) -> Path:
        return Path(str(self.aik_images_path / "recovery.img-") + file)

    def get_kernel_name(self, arch: str) -> str:
        """
        Get kernel name of the device
        :param arch: device architecture information from build.prop
        :return: string of the kernel name
        """
        kernel_names = {
            "arm": "zImage",
            "arm64": "Image.gz",
            "x86": "bzImage",
            "x86_64": "bzImage"
        }
        if self.has_kernel:
            try:
                kernel_name = kernel_names[arch]
            except KeyError:
                kernel_name = "zImage"
            if arch in ("arm", "arm64") and (
                    not self.has_dt_image and not self.has_dtb_image):
                kernel_name += "-dtb"
            self.kernel_name = kernel_name
            return kernel_name
        return ""