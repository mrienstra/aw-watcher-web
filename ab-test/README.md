# A/B test: #252 vs #260 (track only while the browser is focused)

[#252] and [#260] both add an opt-in setting for [#140]: stop recording browser activity while the browser isn't focused. The two branches below build test copies of each PR, so you can run both side by side and compare how they handle the same real-world use.

| Branch | Builds | Shows up as |
|---|---|---|
| `ab-test-pr252` | #252 | ActivityWatch Web Watcher (PR 252 test) |
| `ab-test-pr260` | #260 | ActivityWatch Web Watcher (PR 260 test) |

Compared with the PRs themselves, the test copies:

- **Write to their own buckets:** `aw-watcher-web-pr252test_<hostname>` and `aw-watcher-web-pr260test_<hostname>`. Your normal browser bucket is untouched, and ActivityWatch's Activity view ignores these buckets.
- **Start with the focus setting on,** so there's nothing to configure.
- **Have their own Firefox add-on IDs,** so both can load alongside your normal extension.
- **Log more:** timestamped focus and heartbeat logging, plus an optional copy of all console output to a local log server, so you don't need DevTools open.

Your normal aw-watcher-web can keep running alongside them.

**Most wanted:** Linux (any desktop environment or window manager, X11 or Wayland), and Firefox on any OS. So far this has only been tested on Chrome on macOS.

## Requirements

- ActivityWatch running, with a working window watcher. Its data is what the test copies are measured against. On Wayland, the standard `aw-watcher-window` may not work; use one that does, such as [awatcher](https://github.com/2e3s/awatcher).
- git, and Node.js 20.19+ or 22.12+ with npm, to build the extensions.
- Python 3.9 or later.

On Windows, run the build steps in Git Bash or WSL, and use `py` instead of `python3`.

## 1. Build both

```sh
git clone --recurse-submodules https://github.com/mrienstra/aw-watcher-web.git aw-ab-test
cd aw-ab-test
git checkout ab-test-pr252 && npm ci
for b in pr252 pr260; do
  git checkout ab-test-$b
  VITE_TARGET_BROWSER=chrome npx vite build     # Firefox: VITE_TARGET_BROWSER=firefox
  rm -rf ../aw-$b && cp -r build ../aw-$b
done
```

This leaves the two builds in `../aw-pr252` and `../aw-pr260`.

## 2. Install both

- **Chrome / Chromium / Edge / Brave:** open `chrome://extensions`, turn on **Developer mode**, click **Load unpacked**, and select `../aw-pr252`. Then do the same for `../aw-pr260`.
- **Firefox:** open `about:debugging#/runtime/this-firefox`, click **Load Temporary Add-on…**, and select `manifest.json` in `../aw-pr252`. Then do the same for `../aw-pr260`. Each copy opens a "Consent to offline data collection" tab: accept it in both, or they won't record anything. Firefox removes temporary add-ons when it restarts, so load them again after each restart.

Note the time you loaded them; that's your start time for step 5.

On first start, each copy may also create a stray bucket without the hostname, such as `aw-watcher-web-pr252test`. You can ignore it.

## 3. Optional: keep the logs

```sh
nohup python3 ab-test/log-sink.py >/dev/null 2>&1 &
```

Both copies send their console output here. It's appended to `ab-test/focus-logs/focus-<date>.log`, with each line tagged `pr252` or `pr260`. The server listens on `127.0.0.1` only; stop it with `pkill -f ab-test/log-sink.py`. If it isn't running, the extensions work normally and the lines are simply dropped.

The logs contain URLs and page titles, so don't post them as they are.

## 4. Use your computer normally for a day or more

Switch between apps and between browser windows, and lock or sleep the machine as you usually would. If you use several browser profiles, switch between them too.

## 5. Measure

```sh
python3 ab-test/focus-coverage.py --start <start time, e.g. 2026-10-21T09:00> --browser pr252test_ --app 'chrome|chromium'
python3 ab-test/focus-coverage.py --start <start time> --browser pr260test_ --app 'chrome|chromium'
```

`--start` is your local time. `--app` is a case-insensitive regex for your browser's app name as the window watcher reports it: use `'chrome|chromium'` for Chrome or Chromium, `firefox` for Firefox, `brave` for Brave, and `edge` for Edge. If the script finds no focused-browser time, check the app name in the ActivityWatch Timeline.

If you used windows the extensions can't see, leave them out with `--exclude-title <regex>`. Examples are another browser profile without the extension, and private windows, unless you've allowed the extension in them.

The output contains only numbers and times, no URLs or titles. For each copy it shows:

- how much focused-browser time was covered by web events
- how much web time was recorded while the browser wasn't focused
- any focused stretches of a minute or more that were mostly missed

## 6. Share your results

Please post both outputs in a comment on [#140], along with:

- your OS and version
- desktop environment or window manager, and X11 or Wayland
- browser and version
- roughly how long you ran the test

If one copy missed time that the other covered, the log lines around those times are the most useful thing to add. Please redact URLs and titles first.

## Clean up

1. Remove the two test extensions.
2. Stop the log server, if you started it.
3. Delete the test buckets in ActivityWatch, under **Raw Data**.

[#140]: https://github.com/ActivityWatch/aw-watcher-web/issues/140
[#252]: https://github.com/ActivityWatch/aw-watcher-web/pull/252
[#260]: https://github.com/ActivityWatch/aw-watcher-web/pull/260
