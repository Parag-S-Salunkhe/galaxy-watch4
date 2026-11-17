# Part 5: Getting the always-on display onto the low-power chip

This was the part I enjoyed most.

## The problem

The Galaxy Watch 4 has a small low-power display chip that can draw the always-on display (AOD) while the main processor sleeps. My first face showed a **blank AOD**, and once it did show, it was being drawn by the **main processor**. The watch tried to hand it to the low-power chip and failed every ~8 seconds. More CPU and more battery for a screen that should cost almost nothing.

## Reading the logs

```bash
adb -s "$WATCH" logcat | grep -i -E "offload|NOT_OFFLOADABLE|AmbientDream"
```

The line that mattered:

```
DWF:OffloadScene: [NOT_OFFLOADABLE] Node has a timeDataSource
```

## Finding the cause, one element at a time

We built test versions of the face, each with one element removed (a bisect), and watched the log after each install.

The finding: **if any element of the face reads time data, the watch refuses the hand-off.** That includes text built from the date (`[DAY]`, `[DAY_OF_WEEK_S]`, `[MONTH_S]`), from the hour (`[HOUR_0_23]`) or from the am/pm string, used in templates or expressions. And it checks the **whole** face, including the screen-on layer that is hidden while the AOD shows.

Clock hands and digital clocks are fine. Time zone "Localization" options are only skipped, not blocking.

## The fixes

1. **Date:** instead of building the date text from time data, the face uses the watch's own system **complications** `DAY_OF_WEEK` and `DATE` in fixed slots (not user-editable). The system supplies the text, so the face itself reads no time data.
2. **am/pm for the second time zone:** a digital clock showing the hour in 24-hour format (`hh` with `hourFormat` 24, localised to that time zone), drawn with a **BitmapFont** whose "words" `00`–`11` are an "am" image and `12`–`23` are a "pm" image. The format `HH` fails the validator; `hh` + 24-hour works.
3. Small layout fixes: widen the AOD date window for the longer complication text, and re-centre the second-time-zone digits.

## The result

```
onDisplayOffloadStateSuccess ... OFFLOADED
```

The AOD now runs on the low-power chip and looks the same: date window, second time zone with am/pm, accent hands.

I couldn't measure the battery saving in numbers. Off the charger, the watch's Wi-Fi sleeps and adb goes offline, and a `sleep` in a script on the watch stalls because the CPU is suspended. That's fine: the log says what we needed to know.

## Two more AOD facts

- The AOD switches off when the watch is off the wrist (`AmbientDream: Early exit ... reason=offbody`). That's by design.
- Samsung's own logs say every face, stock ones included, runs the AOD "AP only" on this firmware, so the stock face showing am/pm is not proof that it's offloaded. Trust the `OFFLOADED` line, not the look.

Back to: [README](../README.md) · See also [Do's and Don'ts](Dos-and-Donts.md)
