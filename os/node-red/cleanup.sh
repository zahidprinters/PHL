#!/bin/sh
# Cleanup pass 2026-10-14: remove debug artifacts of previous sessions.
# KEEP: restart_ff.sh (kiosk tool), X/GNOME config, .mozilla profile
# (minus crash dumps + caches), standard XDG dirs, shell dotfiles.
cd /root || exit 1
cp restart_ff.sh /tmp/ffkeeper.sh 2>/dev/null
rm -f /root/*.log /root/*.out /root/*.txt /root/*.png /root/*.sh /root/*.py /root/*.json '/root/;'
cp /tmp/ffkeeper.sh /root/restart_ff.sh 2>/dev/null
rm -f /tmp/ffkeeper.sh
# rotated/compressed logs only, keep live files
find /var/log -type f -name '*.gz' -delete 2>/dev/null
find /var/log -type f -name '*.[0-9]' -delete 2>/dev/null
find /var/log -type f -name '*.[0-9][0-9]' -delete 2>/dev/null
# apt caches (26M): safe, no package removal
apt-get clean 2>/dev/null
apt-get autoclean 2>/dev/null
# firefox crash dumps + page caches
rm -rf /root/.mozilla/firefox/*/minidumps/* /root/.mozilla/firefox/*/crashreports/* 2>/dev/null
rm -rf /root/.mozilla/firefox/*/cache2/* 2>/dev/null
rm -rf /root/.cache/* 2>/dev/null
sync
echo "=== after cleanup ==="
ls /root/
echo "--- disk:"
df -h / /data | tail -2
