import { describe, expect, it } from "vitest";
import {
  createPersianDate,
  jalaliDateTimeToUtcIso,
  toGregorianDateString,
} from "./index";

describe("Jalali date conversion", () => {
  it("converts a Persian calendar date to the expected Gregorian date", () => {
    const date = createPersianDate(1405, 7, 21);

    expect(toGregorianDateString(date)).toBe("2026-10-13");
  });

  it("converts Tehran local date and time to a UTC ISO string", () => {
    const date = createPersianDate(1405, 7, 21);

    // Tehran is UTC+03:30 for this date: 09:30 local is 06:00 UTC.
    expect(jalaliDateTimeToUtcIso(date, 9, 30)).toBe(
      "2026-10-13T06:00:00.000Z",
    );
  });

  it("rejects invalid hours and minutes", () => {
    const date = createPersianDate(1405, 7, 21);

    expect(() => jalaliDateTimeToUtcIso(date, 24, 0)).toThrow(RangeError);
    expect(() => jalaliDateTimeToUtcIso(date, 10, 60)).toThrow(RangeError);
  });
});
