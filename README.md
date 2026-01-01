# Parris Piano App

Utility stack for the Yamaha CVP-301 (ordered most to least useful for setup and daily use).

1. `CVP301\um3141x64\um3141x64\setup.exe` - Yamaha USB-MIDI driver; required for stable USB connection.
2. `CVP301\cvp301_v180.zip` - CVP-301 firmware v1.80; update before heavy MIDI work.
3. `CVP301\Cakewalk_Product_Center_Setup_1.1.0.004.exe` - Full DAW (Cakewalk) for recording/editing MIDI/audio.
4. `CVP301\tracktion_download_manager_v1.5.3.exe` - Fetches Tracktion/Waveform DAW as an alternative workflow.
5. `CVP301\astudio.msi` - Anvil Studio, lightweight MIDI sequencer for quick edits.
6. `CVP301\MuseScore_Studio_Installer_via_MuseHub.exe` and `MuseScore Studio 4.lnk` - Notation/scoring via MIDI import/export.
7. `CVP301\Synthesia-10.9-installer.exe` - Practice/learning app using the CVP as MIDI I/O.
8. `CVP301\SeeMusic 7.6.2.exe` - Performance visualizer/recorder.
9. `testingMidi\MIDIVisualizer\` - Open-source MIDI visualizer (needs build; similar to SeeMusic).
10. `CVP301\freepiano_2.2.2.1_win64\freepiano.exe` - Virtual piano/MIDI router.
11. `CVP301\Midi Piano Installer.exe` - Simple MIDI piano app; overlaps with FreePiano.
12. `CVP301\LLMidi\LLMidi.vst3` - Experimental VST for DAW hosting.
13. `CVP301\Embers-2.3-windows.exe` - Likely a visualizer; niche unless you need it.
14. `CVP301\asinstall.exe` - Unknown/legacy utility; keep aside unless needed.
15. `CVP301\setup.exe` (440 KB) - Small helper from driver zip; redundant after main driver install.

Next steps:
- Install the Yamaha USB-MIDI driver, then update the CVP firmware.
- Pick a DAW (Cakewalk or Tracktion), then add your preferred practice/visualizer tool.

## CVP Tutor desktop app (Windows)
- Easiest start: double-click `start_cvp_tutor.bat` (handles venv + deps, then launches).
- Manual: 
  - `cd cvp_tutor`
  - `python -m venv .venv`
  - `.venv\Scripts\activate`
  - `pip install -r requirements.txt`
  - `python app.py`
- Build one-file exe: `.\build.ps1`
- Features: MIDI in/out selection, Test Tone, load .mid, tempo/transpose/loop, Tutor wait-mode, learning part selection, logging to `logs/app.log`.
## CVP Tutor desktop app (Windows)
- Code lives in `cvp_tutor/`. Launch with:
  - `cd cvp_tutor`
  - `python -m venv .venv`
  - `.venv\Scripts\activate`
  - `pip install -r requirements.txt`
  - `python app.py`
- Build one-file exe: `.uild.ps1`
- Features: MIDI in/out selection, Test Tone, load .mid, tempo/transpose/loop, Tutor wait-mode, learning part selection, logging to `logs/app.log`.
