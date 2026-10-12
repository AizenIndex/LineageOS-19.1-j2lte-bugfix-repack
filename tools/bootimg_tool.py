#!/usr/bin/env python3
"""
Samsung Exynos 3475 Boot Image and Ramdisk Tool
Supports:
- Unpacking / repacking Android boot images with Samsung DTBH device tree table
- Unpacking / repacking ramdisk (XZ and Gzip compression)
- Creating Odin-flashable .tar.md5 packages
"""

import os
import sys
import struct
import lzma
import gzip
import io
import hashlib

def pages(size, page_size):
    return (size + page_size - 1) // page_size * page_size

def pad(data, page_size):
    rem = len(data) % page_size
    return data + (b'\0' * (page_size - rem) if rem else b'')

def unpack_boot(boot_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    with open(boot_path, 'rb') as f:
        hdr = f.read(2048)
        if hdr[:8] != b'ANDROID!':
            raise ValueError(f'{boot_path} is not a valid Android boot image!')
        
        k_size, k_addr, r_size, r_addr, s_size, s_addr, tags_addr, page_size, dt_size, os_version = struct.unpack('<10I', hdr[8:48])
        name = hdr[48:64].split(b'\0')[0].decode('latin1', errors='replace')
        cmdline = hdr[64:576].split(b'\0')[0].decode('latin1', errors='replace')
        
        base = k_addr - 0x00008000
        kernel_offset = k_addr - base
        ramdisk_offset = r_addr - base
        second_offset = s_addr - base
        tags_offset = tags_addr - base
        
        with open(os.path.join(out_dir, 'boot.img-base'), 'w') as bf: bf.write(f'{hex(base)}\n')
        with open(os.path.join(out_dir, 'boot.img-kerneloff'), 'w') as kof: kof.write(f'{hex(kernel_offset)}\n')
        with open(os.path.join(out_dir, 'boot.img-ramdiskoff'), 'w') as rof: rof.write(f'{hex(ramdisk_offset)}\n')
        with open(os.path.join(out_dir, 'boot.img-tagsoff'), 'w') as tof: tof.write(f'{hex(tags_offset)}\n')
        with open(os.path.join(out_dir, 'boot.img-pagesize'), 'w') as pf: pf.write(f'{page_size}\n')
        with open(os.path.join(out_dir, 'boot.img-cmdline'), 'w') as cf: cf.write(cmdline)
        with open(os.path.join(out_dir, 'boot.img-osversion'), 'w') as ovf: ovf.write(f'{hex(os_version)}\n')
        with open(os.path.join(out_dir, 'boot.img-board'), 'w') as nf: nf.write(name)
        
        k_pos = page_size
        r_pos = k_pos + pages(k_size, page_size)
        s_pos = r_pos + pages(r_size, page_size)
        dt_pos = s_pos + pages(s_size, page_size)
        
        f.seek(k_pos)
        with open(os.path.join(out_dir, 'boot.img-zImage'), 'wb') as kf:
            kf.write(f.read(k_size))
            
        f.seek(r_pos)
        r_data = f.read(r_size)
        ext = 'xz' if r_data[:6] == b'\xfd7zXZ\x00' else 'gz'
        ramdisk_filename = f'boot.img-ramdisk.cpio.{ext}'
        with open(os.path.join(out_dir, ramdisk_filename), 'wb') as rf:
            rf.write(r_data)
            
        if s_size > 0:
            f.seek(s_pos)
            with open(os.path.join(out_dir, 'boot.img-second'), 'wb') as sf:
                sf.write(f.read(s_size))
                
        if dt_size > 0:
            f.seek(dt_pos)
            with open(os.path.join(out_dir, 'boot.img-dtb'), 'wb') as df:
                df.write(f.read(dt_size))
                
    print(f'[+] Unpacked {boot_path} -> {out_dir}')
    print(f'    - Kernel (zImage): {k_size} bytes')
    print(f'    - Ramdisk ({ext.upper()}): {r_size} bytes ({ramdisk_filename})')
    print(f'    - Device Tree (DTB): {dt_size} bytes')
    return out_dir

def unpack_ramdisk(ramdisk_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    with open(ramdisk_path, 'rb') as f:
        raw = f.read()
    if raw[:6] == b'\xfd7zXZ\x00':
        decomp = lzma.decompress(raw)
    elif raw[:2] == b'\x1f\x8b':
        decomp = gzip.decompress(raw)
    else:
        decomp = raw
        
    bio = io.BytesIO(decomp)
    count = 0
    while True:
        hdr = bio.read(110)
        if len(hdr) < 110: break
        if hdr[:6] not in (b'070701', b'070702'): break
        mode = int(hdr[14:22], 16)
        filesize = int(hdr[54:62], 16)
        namesize = int(hdr[94:102], 16)
        name = bio.read(namesize)[:-1].decode('latin1', errors='replace')
        pad1 = (4 - ((110 + namesize) % 4)) % 4
        bio.read(pad1)
        if name == 'TRAILER!!!': break
        
        target = os.path.join(out_dir, name.replace('/', os.sep))
        is_dir = (mode & 0o170000) == 0o040000
        if is_dir:
            os.makedirs(target, exist_ok=True)
        else:
            parent = os.path.dirname(target)
            if parent: os.makedirs(parent, exist_ok=True)
            with open(target, 'wb') as fp:
                fp.write(bio.read(filesize))
        pad2 = (4 - (filesize % 4)) % 4
        bio.read(pad2)
        count += 1
    print(f'[+] Extracted {count} ramdisk items -> {out_dir}')
    return count

def repack_ramdisk(in_dir, out_path, format='xz'):
    buf = io.BytesIO()
    ino = 1
    entries = []
    for root, dirs, files in os.walk(in_dir):
        rel_root = os.path.relpath(root, in_dir)
        if rel_root != '.':
            entries.append((rel_root.replace('\\', '/'), 0o40755, b''))
        for f in files:
            rel_file = os.path.normpath(os.path.join(rel_root, f) if rel_root != '.' else f).replace('\\', '/')
            full = os.path.join(root, f)
            with open(full, 'rb') as fp: data = fp.read()
            mode = 0o100750 if f == 'init' else 0o100644
            entries.append((rel_file, mode, data))
            
    entries.sort(key=lambda x: x[0])
    for name, mode, data in entries:
        namesize = len(name) + 1
        filesize = len(data)
        hdr_str = f'070701{ino:08X}{mode:08X}{0:08X}{0:08X}{1:08X}{0:08X}{filesize:08X}{0:08X}{0:08X}{0:08X}{0:08X}{namesize:08X}{0:08X}'.encode('ascii')
        buf.write(hdr_str)
        buf.write(name.encode('latin1') + b'\0')
        buf.write(b'\0' * ((4 - ((110 + namesize) % 4)) % 4))
        if filesize > 0:
            buf.write(data)
            buf.write(b'\0' * ((4 - (filesize % 4)) % 4))
        ino += 1
        
    trailer = 'TRAILER!!!'
    namesize = len(trailer) + 1
    buf.write(f'070701{0:08X}{0:08X}{0:08X}{0:08X}{1:08X}{0:08X}{0:08X}{0:08X}{0:08X}{0:08X}{0:08X}{namesize:08X}{0:08X}'.encode('ascii'))
    buf.write(trailer.encode('latin1') + b'\0')
    buf.write(b'\0' * ((4 - ((110 + namesize) % 4)) % 4))
    
    rem = buf.tell() % 512
    if rem != 0: buf.write(b'\0' * (512 - rem))
    raw = buf.getvalue()
    
    if format == 'xz':
        compressed = lzma.compress(raw, check=lzma.CHECK_CRC32)
    elif format == 'gz':
        compressed = gzip.compress(raw, mtime=0)
    else:
        compressed = raw
        
    with open(out_path, 'wb') as fp: fp.write(compressed)
    print(f'[+] Repacked ramdisk ({format.upper()}) -> {out_path} ({len(compressed)} bytes)')
    return out_path

def repack_boot(unpacked_dir, out_boot_path):
    with open(os.path.join(unpacked_dir, 'boot.img-base')) as f: base = int(f.read().strip(), 16)
    with open(os.path.join(unpacked_dir, 'boot.img-kerneloff')) as f: kernel_offset = int(f.read().strip(), 16)
    with open(os.path.join(unpacked_dir, 'boot.img-ramdiskoff')) as f: ramdisk_offset = int(f.read().strip(), 16)
    with open(os.path.join(unpacked_dir, 'boot.img-tagsoff')) as f: tags_offset = int(f.read().strip(), 16)
    with open(os.path.join(unpacked_dir, 'boot.img-pagesize')) as f: page_size = int(f.read().strip())
    with open(os.path.join(unpacked_dir, 'boot.img-cmdline')) as f: cmdline = f.read().strip()
    with open(os.path.join(unpacked_dir, 'boot.img-osversion')) as f: os_version = int(f.read().strip(), 16)
    with open(os.path.join(unpacked_dir, 'boot.img-board')) as f: board_name = f.read().strip()
    
    with open(os.path.join(unpacked_dir, 'boot.img-zImage'), 'rb') as f: kernel_data = f.read()
    
    rd_candidates = ['new-ramdisk.cpio.xz', 'boot.img-ramdisk.cpio.xz', 'new-ramdisk.gz', 'boot.img-ramdisk.cpio.gz', 'new-ramdisk.cpio']
    rd_file = next((os.path.join(unpacked_dir, c) for c in rd_candidates if os.path.exists(os.path.join(unpacked_dir, c))), None)
    if not rd_file:
        raise FileNotFoundError('No ramdisk found in ' + unpacked_dir)
    with open(rd_file, 'rb') as f: ramdisk_data = f.read()
    
    dtb_file = os.path.join(unpacked_dir, 'boot.img-dtb')
    dtb_data = b''
    if os.path.exists(dtb_file):
        with open(dtb_file, 'rb') as f: dtb_data = f.read()
        
    k_addr = base + kernel_offset
    r_addr = base + ramdisk_offset
    tags_addr = base + tags_offset
    s_addr = 0
    s_size = 0
    k_size = len(kernel_data)
    r_size = len(ramdisk_data)
    dt_size = len(dtb_data)
    
    hdr = bytearray(2048)
    hdr[:8] = b'ANDROID!'
    struct.pack_into('<10I', hdr, 8, k_size, k_addr, r_size, r_addr, s_size, s_addr, tags_addr, page_size, dt_size, os_version)
    name_bytes = board_name.encode('latin1')[:16]
    hdr[48:48+len(name_bytes)] = name_bytes
    cmd_bytes = cmdline.encode('latin1')[:512]
    hdr[64:64+len(cmd_bytes)] = cmd_bytes
    
    sha = hashlib.sha1()
    sha.update(kernel_data)
    sha.update(struct.pack('<I', k_size))
    sha.update(ramdisk_data)
    sha.update(struct.pack('<I', r_size))
    if dt_size > 0:
        sha.update(dtb_data)
        sha.update(struct.pack('<I', dt_size))
    digest = sha.digest()
    hdr[576:576+len(digest)] = digest
    
    with open(out_boot_path, 'wb') as out:
        out.write(pad(hdr, page_size))
        out.write(pad(kernel_data, page_size))
        out.write(pad(ramdisk_data, page_size))
        if dt_size > 0:
            out.write(pad(dtb_data, page_size))
            
    print(f'[+] Repacked boot image -> {out_boot_path} ({os.path.getsize(out_boot_path)} bytes)')
    return out_boot_path

def make_odin_tar(boot_img_path, out_tar_path):
    import tarfile
    with tarfile.open(out_tar_path, 'w', format=tarfile.USTAR_FORMAT) as tar:
        tar.add(boot_img_path, arcname=os.path.basename(boot_img_path))
    md5 = hashlib.md5(open(out_tar_path, 'rb').read()).hexdigest()
    with open(out_tar_path, 'ab') as f:
        f.write(f'  {os.path.basename(out_tar_path)}\n'.encode('latin1'))
    print(f'[+] Created Odin flashable package: {out_tar_path} (MD5: {md5})')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage:')
        print('  bootimg_tool.py unpack-boot <boot.img> <out_dir>')
        print('  bootimg_tool.py unpack-ramdisk <ramdisk_path> <out_dir>')
        print('  bootimg_tool.py repack-ramdisk <in_dir> <out_ramdisk_path> [xz|gz]')
        print('  bootimg_tool.py repack-boot <unpacked_dir> <out_boot.img>')
        print('  bootimg_tool.py make-odin-tar <boot.img> <out.tar.md5>')
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == 'unpack-boot': unpack_boot(sys.argv[2], sys.argv[3])
    elif cmd == 'unpack-ramdisk': unpack_ramdisk(sys.argv[2], sys.argv[3])
    elif cmd == 'repack-ramdisk': repack_ramdisk(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else 'xz')
    elif cmd == 'repack-boot': repack_boot(sys.argv[2], sys.argv[3])
    elif cmd == 'make-odin-tar': make_odin_tar(sys.argv[2], sys.argv[3])
