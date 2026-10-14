// Node-RED settings for the ECU-30 HMI — RECORD OF THE BOARD PATCH.
// The live file is the STOCK DEFAULT settings.js, edited in place:
//   board:  /data/chroot14/data/nodered/settings.js
//           (same file as /data/nodered/settings.js from inside the chroot)
//   backup: settings.js.bak-v1 next to it (pre-v1 copy)
// Only two lines differ from stock:
//     httpAdminRoot: '/red',              // editor off / so the SPA owns the root
//     httpStatic: '/data/nodered/static/',// ABSOLUTE from the CHROOT'S view
// A host-absolute path (/data/chroot14/...) 404s (node cannot see it), and a
// relative path resolves against process.cwd() (the upstart cwd, NOT userDir).
// Flow file stays flows_linaro-ubuntu-desktop.json (the upstart --userDir
// default for this user; see os/node-red/nodered.conf and ARCHITECTURE.md).
