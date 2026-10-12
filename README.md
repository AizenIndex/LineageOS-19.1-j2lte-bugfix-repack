# LineageOS 19.1 (Android 12.1 Go) — Community Bugfix Repack

### For Samsung Galaxy J2 (`j2lte` / `SM-J200G` / Exynos 3475)

[![Device](https://img.shields.io/badge/Device-Samsung%20Galaxy%20J2%20(SM--J200G)-blue.svg)](#)
[![Android Version](https://img.shields.io/badge/Android-12.1%20Go%20(LineageOS%2019.1)-green.svg)](#)
[![Latest Release](https://img.shields.io/badge/Release-v1.0--bugfix-purple.svg?logo=github)](https://github.com/AizenIndex/LineageOS-19.1-j2lte-bugfix-repack/releases/tag/v1.0-bugfix)
[![Download ROM](https://img.shields.io/badge/Download-ROM%20ZIP%20(544%20MB)-brightgreen.svg?logo=android)](https://github.com/AizenIndex/LineageOS-19.1-j2lte-bugfix-repack/releases/download/v1.0-bugfix/lineage-19.1-20261012-UNOFFICIAL-j2lte.zip)
[![Status](https://img.shields.io/badge/Status-Stable%20%2F%20Tested-brightgreen.svg)](#)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-orange.svg)](https://buymeacoffee.com/aizenindex)

---

> [!NOTE]
> **Credits & Attribution:**  
> This release is a **community bugfix repack**. The base LineageOS 19.1 ROM was ported and created by [@lavenly](https://github.com/lavenly). Full credit for the initial ROM bring-up and tree development belongs to him!  
> Original XDA Thread: [ROM Unofficial 12.1 LineageOS 19.1 for Galaxy J2 2015](https://xdaforums.com/t/rom-unofficial-12-1-lineageos-19-1-for-galaxy-j2-2015-exynos-3475.4803661/)

---

## 🛠️ What Was Fixed in This Repack

### 1. Front Camera Sensor Fix (Siliconfile SR200)
- **Problem:** On hardware revision 4 of the SM-J200G, the front camera failed to initialize and caused `cameraserver` crashes whenever switching to the front sensor.
- **Root Cause:** The device tree source (`exynos3475-j2lte_swa_open_04.dts`) omitted `front_sensor_id`, defaulting to `303` (Dongbu DB8221A at I2C `0x45`). Probing this sensor returned `-ENXIO` (-6). The actual physical hardware sensor is **Siliconfile SR200** (`SENSOR_NAME_SR200 = 302`, I2C address `0x20`).
- **Solution:** Patched the DTS node `fimc_is@14400000` with `front_sensor_id = <302>;` across revisions 2, 3, and 4.
- **Result:** Both rear and front cameras work smoothly in Open Camera, capturing full-resolution photos and recording videos.
- **Diff:** See [`patches/0001-ARM-dts-exynos3475-j2lte-set-front_sensor_id-to-302-SR200.patch`](patches/0001-ARM-dts-exynos3475-j2lte-set-front_sensor_id-to-302-SR200.patch).

---

### 2. Overheating, Bootloops, & Thermal Runaway Guard
- **Problem:** The device frequently froze, overheated rapidly (>70°C), and suffered from bootloops or sudden emergency PMIC thermal shutdowns during app launches or charging.
- **Root Cause:** Unregulated 1.5 GHz CPU bursts combined with aggressive interactive governor ramp-ups generated heat faster than the passive copper shield on the Exynos 3475 could dissipate.
- **Solution:**
  - Hard-clamped `scaling_max_freq` and `cpufreq_max_limit` to `897000` (897 MHz) in `init.universal3475.rc`.
  - Tuned the interactive governor parameters:
    - `hispeed_freq = 507000`
    - `go_hispeed_load = 95`
    - `above_hispeed_delay = 80000`
    - `target_loads = 85 507000:95 897000:99`
  - Re-balanced `powerhint.json` thresholds.
- **Result:** Operating temperatures remain stable at **55–62°C** under sustained load, eliminating thermal trip reboots while preserving responsive UI performance.
- **Diff:** See [`patches/0002-universal3475-common-optimize-interactive-governor-and-init.patch`](patches/0002-universal3475-common-optimize-interactive-governor-and-init.patch).

---

### 3. Built-in KernelSU & Root App Compatibility
- **Kernel Driver:** KernelSU driver (`CONFIG_KSU=y`, version `32651-4`) is integrated into `boot.img`.
- **Manager App:** Patched KernelSU Manager is pre-installed into `/system/app/KernelSU/` with Dalvik UAPI checks bypassed.
- **Result:** No "Kernel update required" warning banner; full access to **Home**, **Superuser**, **Modules**, and **Settings** tabs; hardware tuning tools such as `hKtweaks` grant root permissions out of the box.

---

### 4. Settings Wi-Fi QR Code Scanner & Camera HAL Stabilization
- **Problem:** Wi-Fi QR code scanning in Settings caused black preview frames, continuous lens autofocus hunting, and intense CPU heat and battery discharge.
- **Root Cause & Fixes:**
  - **Color Format Crash:** Added NEON software YUYV -> NV21 conversion fallback in `libcsc.so`.
  - **Aspect Ratio Distortion:** Patched preview resolution table in `libexynoscameraexternal.so` to 720x720 (1:1 square).
  - **Focus Motor Hunting:** Throttled hardware autofocus sweep to 3.0-second intervals (`mod 2`) in `camera.universal3475.so`.
  - **CPU & GC Overload:** Optimized Settings app (`QrCamera`): inserted 50ms decode throttle (reducing CPU usage by >60%), eliminated heap churn in `crop()`, enabled `TRY_HARDER` for dense fiber QR codes, and bypassed scan cache false alarms.
- **Result:** Fast, smooth 60 FPS preview with cool thermals; scans Wi-Fi QR codes and connects instantly.
- **Scanning Distance Note:** For optimal recognition, hold the camera at **15 to 20 cm** (more than 10 cm away). The J2 rear lens has a physical minimum focus limit of ~10–12 cm; holding it closer than 10 cm softens the image and cuts off the mandatory QR white border ("Quiet Zone"). At 15–20 cm, it locks on and connects instantly.

---

## 📥 Downloads

Download the flashable ROM zip directly from the **[GitHub Releases](https://github.com/AizenIndex/LineageOS-19.1-j2lte-bugfix-repack/releases/tag/v1.0-bugfix)** page:

| File | Size | Direct Download |
| :--- | :--- | :--- |
| **`lineage-19.1-20261012-UNOFFICIAL-j2lte.zip`** | 563 MB (590,941,531 bytes) | 🚀 **[Download ROM ZIP](https://github.com/AizenIndex/LineageOS-19.1-j2lte-bugfix-repack/releases/download/v1.0-bugfix/lineage-19.1-20261012-UNOFFICIAL-j2lte.zip)** |

- **Release Tag:** [`v1.0-bugfix`](https://github.com/AizenIndex/LineageOS-19.1-j2lte-bugfix-repack/releases/tag/v1.0-bugfix)
- **Status:** Verified working on physical hardware (SM-J200G rev 4).

---

## 📲 Installation Instructions

1. Boot into TWRP Recovery on your Samsung Galaxy J2 (`SM-J200G`).
2. Make a full Nandroid backup of your existing partitions (System, Data, Boot, EFS).
3. Wipe: `Dalvik / ART Cache`, `Cache`, `System`, and `Data` (Clean flash strongly recommended).
4. Flash `lineage-19.1-20261012-UNOFFICIAL-j2lte.zip`.
5. *(Optional)* Flash GApps (MindTheGapps 12.1 ARM) if you need Google Play Services.
6. Reboot system and enjoy your stable Galaxy J2!

---

## ☕ Support

If this bugfix repack saved your phone and made it usable as a daily driver, you can support my work:

[![Buy Me A Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/aizenindex)

*Please also visit the original thread and thank [@lavenly](https://github.com/lavenly) for the ROM port!*
