## LineageOS 19.1 Unofficial Bugfix Repack for Samsung Galaxy J2 (`SM-J200G` / `j2lte`)

This is a **community bugfix repack** for LineageOS 19.1 (Android 12.1 Go).  
All original ROM porting and tree development credits go to **@lavenly** ([Original XDA Thread](https://xdaforums.com/t/rom-unofficial-12-1-lineageos-19-1-for-galaxy-j2-2015-exynos-3475.4803661/)).

---

### 🛠️ What Was Fixed in This Repack:

1. **Front Camera Sensor Fix (Siliconfile SR200 Sensor ID 302):**
   - Fixed hardware revision 4 DTB omitting `front_sensor_id`, which previously caused `-ENXIO` (-6) and crashed `cameraserver`.
   - Both front and rear cameras now capture full-resolution photos and record video cleanly in Open Camera.

2. **Thermals & Bootloop Elimination:**
   - Clamped CPU `scaling_max_freq` safely at 897 MHz in `init.universal3475.rc`.
   - Tuned interactive CPU governor ramp rates and target loads to prevent thermal runaway.
   - Device runs cool (55–62°C) without freezing or emergency PMIC thermal shutdowns.

3. **KernelSU Pre-installed & Working Out of the Box:**
   - Kernel driver built-in (`CONFIG_KSU=y`).
   - Pre-installed patched KernelSU Manager into `/system/app/KernelSU/` with bypassed UAPI errors.
   - Full access to Home, Superuser, Modules, and Settings.
   - Hardware tuning apps like `hKtweaks` grant root permissions right away.

---

### 📦 File Details:
- **File Name:** `lineage-19.1-20261012-UNOFFICIAL-j2lte.zip`
- **File Size:** `570,384,701 bytes` (544 MB)
- **Status:** Tested & 100% verified on physical SM-J200G hardware.

---

### ☕ Support & Donations:
If this bugfix repack saved your Galaxy J2, feel free to support:  
👉 **[Buy Me a Coffee](https://buymeacoffee.com/aizenindex)**  
*(And make sure to thank @lavenly for the base ROM port!)*
