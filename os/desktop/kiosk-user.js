// Firefox 52 kiosk profile prefs — installed as
// /root/.mozilla/firefox/fdg2sjwb.default/user.js (applied on every start).
// Kills every prompt/infobar/telemetry that could appear over the dashboard.
user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("browser.sessionstore.resume_from_crash", false);
user_pref("browser.sessionstore.max_resumed_crashes", -1);
user_pref("browser.warnOnQuit", false);
user_pref("browser.tabs.warnOnClose", false);
user_pref("browser.startup.homepage", "http://localhost:1880/ui");
user_pref("browser.startup.page", 0);
user_pref("browser.newtabpage.enabled", false);
user_pref("datareporting.policy.dataSubmissionEnabled", false);
user_pref("datareporting.healthreport.uploadEnabled", false);
user_pref("toolkit.telemetry.enabled", false);
user_pref("toolkit.telemetry.reportingpolicy.firstRun", false);
user_pref("app.update.disabledForTesting", true);
user_pref("app.update.auto", false);
user_pref("extensions.update.enabled", false);
user_pref("browser.uitour.enabled", false);
user_pref("app.shield.optoutstudies.enabled", false);
user_pref("browser.safebrowsing.enabled", false);
user_pref("browser.safebrowsing.malware.enabled", false);
user_pref("full-screen-api.warning.timeout", 0);
