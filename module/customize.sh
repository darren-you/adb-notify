#!/system/bin/sh

ui_print "- USB Notify Toggle"
ui_print "- Default mode: hide USB debugging and USB charging notifications"

if [ ! -f "$MODPATH/config" ]; then
  echo "notify=0" > "$MODPATH/config"
fi

set_perm "$MODPATH/common.sh" 0 0 0644
set_perm "$MODPATH/post-fs-data.sh" 0 0 0755
set_perm "$MODPATH/service.sh" 0 0 0755
set_perm "$MODPATH/action.sh" 0 0 0755
set_perm "$MODPATH/uninstall.sh" 0 0 0755
set_perm "$MODPATH/config" 0 0 0644
set_perm "$MODPATH/build.json" 0 0 0644
set_perm "$MODPATH/system/bin/usb-adb-notify" 0 0 0755

MODDIR="$MODPATH"
. "$MODPATH/common.sh"
apply_notify "$(read_notify)"

ui_print "- Use: su -c usb-adb-notify status"
ui_print "- Use: su -c usb-adb-notify off"
ui_print "- Use: su -c usb-adb-notify on"
