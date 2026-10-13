import {
  CalendarDate,
  CalendarDateTime,
  GregorianCalendar,
  PersianCalendar,
  Time,
  toCalendar,
  toZoned,
} from "@internationalized/date";

export const BOOKITO_TIME_ZONE = "Asia/Tehran";
export const PERSIAN_LOCALE = "fa-IR-u-ca-persian-nu-arabext";

/** Returns a date object whose calendar system is Persian/Jalali. */
export function createPersianDate(
  year: number,
  month: number,
  day: number,
): CalendarDate {
  return new CalendarDate(new PersianCalendar(), year, month, day);
}

/** Converts a selected Jalali calendar date to its Gregorian YYYY-MM-DD equivalent. */
export function toGregorianDateString(date: CalendarDate): string {
  return toCalendar(date, new GregorianCalendar()).toString();
}

/**
 * Converts a Jalali date and a wall-clock time in Asia/Tehran to a UTC ISO string.
 * The timezone conversion is performed by @internationalized/date; do not append `Z`
 * to a local time string manually.
 */
export function jalaliDateTimeToUtcIso(
  date: CalendarDate,
  hour: number,
  minute: number,
  timeZone = BOOKITO_TIME_ZONE,
): string {
  if (!Number.isInteger(hour) || hour < 0 || hour > 23) {
    throw new RangeError("hour must be an integer between 0 and 23");
  }

  if (!Number.isInteger(minute) || minute < 0 || minute > 59) {
    throw new RangeError("minute must be an integer between 0 and 59");
  }

  const localDateTime = new CalendarDateTime(
    date.calendar,
    date.era,
    date.year,
    date.month,
    date.day,
    hour,
    minute,
  );

  return toZoned(localDateTime, timeZone).toDate().toISOString();
}

/** Convenience helper for consumers that prefer the Time value type. */
export function jalaliDateAndTimeToUtcIso(
  date: CalendarDate,
  time: Time,
  timeZone = BOOKITO_TIME_ZONE,
): string {
  return jalaliDateTimeToUtcIso(date, time.hour, time.minute, timeZone);
}
