import zipfile, zlib, hashlib, struct, shutil

apk_in = r"D:\DEVICES\SM-J200G\SMj200G\CUSTOM ROMS\NEW LOS ROMS\19.1\KernelSU_v3.3.0-74_32675-release.apk"
apk_out = "KernelSU_patched.apk"

with zipfile.ZipFile(apk_in, 'r') as z:
    dex = bytearray(z.read('classes.dex'))

# Patch 1: isKernelOutdated check (offset 0x24d196)
off1 = 0x24d196
exp1 = b'\x37\xfe\x05\x00'
rep1 = b'\x28\x05\x00\x00'
assert dex[off1:off1+4] == exp1, f"Mismatch at off1: {dex[off1:off1+4].hex()}"
dex[off1:off1+4] = rep1

# Patch 2: Natives.a() kernel_uapi == manager_uapi check (offset 0x47d3b2)
off2 = 0x47d3b2
exp2 = b'\x33\x20\x0e\x00'
rep2 = b'\x00\x00\x00\x00'
assert dex[off2:off2+4] == exp2, f"Mismatch at off2: {dex[off2:off2+4].hex()}"
dex[off2:off2+4] = rep2

# Recompute SHA1
dex[12:32] = hashlib.sha1(dex[32:]).digest()

# Recompute Adler32
adler = zlib.adler32(dex[12:]) & 0xffffffff
dex[8:12] = struct.pack('<I', adler)

# Rebuild APK with patched classes.dex
with zipfile.ZipFile(apk_in, 'r') as zin, zipfile.ZipFile(apk_out, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        if item.filename == 'classes.dex':
            zout.writestr(item, dex)
        else:
            zout.writestr(item, zin.read(item.filename))

print("KernelSU_patched.apk built successfully!")
