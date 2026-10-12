import os
import sys
import zipfile
import shutil
import time

ORIGINAL_ZIP = r"D:\DEVICES\SM-J200G\SMj200G\CUSTOM ROMS\NEW LOS ROMS\19.1\19.1-20261002-lavenly-j2lte.zip"
OUTPUT_ZIP = "lineage-19.1-20261012-UNOFFICIAL-j2lte.zip"
DEST_ZIP = r"D:\DEVICES\SM-J200G\SMj200G\CUSTOM ROMS\NEW LOS ROMS\19.1\lineage-19.1-20261012-UNOFFICIAL-j2lte.zip"

BOOT_IMG = "boot_patched_cam.img"
SDAT_DIR = r"rom_build\sdat_out"

print("Starting ROM assembly...")
t0 = time.time()

with zipfile.ZipFile(ORIGINAL_ZIP, 'r') as zin, zipfile.ZipFile(OUTPUT_ZIP, 'w') as zout:
    for info in zin.infolist():
        fname = info.filename
        compress_type = info.compress_type

        if fname == 'boot.img':
            print(f"Adding updated {fname} from {BOOT_IMG} (compression: {compress_type})...")
            with open(BOOT_IMG, 'rb') as f:
                data = f.read()
            new_info = zipfile.ZipInfo(fname)
            new_info.compress_type = compress_type
            zout.writestr(new_info, data)

        elif fname == 'system.new.dat.br':
            src = os.path.join(SDAT_DIR, 'system.new.dat.br')
            print(f"Adding updated {fname} from {src} (STORED)...")
            new_info = zipfile.ZipInfo(fname)
            new_info.compress_type = zipfile.ZIP_STORED
            with open(src, 'rb') as f:
                zout.writestr(new_info, f.read())

        elif fname == 'system.transfer.list':
            src = os.path.join(SDAT_DIR, 'system.transfer.list')
            print(f"Adding updated {fname} from {src} (DEFLATED)...")
            new_info = zipfile.ZipInfo(fname)
            new_info.compress_type = zipfile.ZIP_DEFLATED
            with open(src, 'rb') as f:
                zout.writestr(new_info, f.read())

        elif fname == 'system.patch.dat':
            src = os.path.join(SDAT_DIR, 'system.patch.dat')
            print(f"Adding updated {fname} from {src} (STORED)...")
            new_info = zipfile.ZipInfo(fname)
            new_info.compress_type = zipfile.ZIP_STORED
            with open(src, 'rb') as f:
                zout.writestr(new_info, f.read())

        else:
            print(f"Copying {fname} (compression: {compress_type})...")
            data = zin.read(fname)
            new_info = zipfile.ZipInfo(fname)
            new_info.compress_type = compress_type
            zout.writestr(new_info, data)

print(f"Local ROM zip created in {time.time()-t0:.1f}s: {OUTPUT_ZIP} ({os.path.getsize(OUTPUT_ZIP)} bytes)")

print(f"Mirroring to {DEST_ZIP}...")
shutil.copyfile(OUTPUT_ZIP, DEST_ZIP)
print(f"ROM zip mirrored successfully to D: drive!")
