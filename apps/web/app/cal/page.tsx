"use client";

import { useMemo, useState } from "react";
import { Calendar, Label, TimeField } from "@heroui/react";
import { I18nProvider } from "@react-aria/i18n";
import {
  CalendarDate,
  PersianCalendar,
  Time,
  today,
} from "@internationalized/date";

import {
  BOOKITO_TIME_ZONE,
  PERSIAN_LOCALE,
  jalaliDateTimeToUtcIso,
  toGregorianDateString,
} from "@/lib/datetime/index";

const toPersianDigits = (value: string) =>
  value.replace(/\d/g, (digit) => "۰۱۲۳۴۵۶۷۸۹"[Number(digit)]);

const formatTime = (time: Time) =>
  `${String(time.hour).padStart(2, "0")}:${String(time.minute).padStart(2, "0")}`;

export default function CalendarSpikePage() {
  const [selectedDate, setSelectedDate] = useState<CalendarDate | null>(() =>
    today(BOOKITO_TIME_ZONE, new PersianCalendar()),
  );

  const [time, setTime] = useState<Time | null>(new Time(9, 30));

  const result = useMemo(() => {
    if (!selectedDate || !time) return null;

    try {
      return {
        gregorianDate: toGregorianDateString(selectedDate),
        utcISO: jalaliDateTimeToUtcIso(
          selectedDate,
          time.hour,
          time.minute,
          BOOKITO_TIME_ZONE,
        ),
      };
    } catch (error) {
      console.error("Failed to convert the selected date and time:", error);
      return null;
    }
  }, [selectedDate, time]);

  return (
    <main className="mx-auto flex min-h-screen w-full flex-col gap-6 p-6 text-right">
      <header className="space-y-2">
        <p className="text-sm font-medium text-default-500">
          S0-4 · Technical Spike
        </p>

        <h1 className="text-2xl font-bold">آزمایش تقویم جلالی و RTL</h1>

        <p className="text-sm leading-6 text-default-600">
          بررسی تقویم جلالی، شروع هفته از شنبه، ارقام فارسی، دسترس‌پذیری
          صفحه‌کلید و تبدیل ساعت تهران به UTC. این صفحه صرفاً برای آزمایش فنی
          است.
        </p>
      </header>

      <section className="grid gap-8 rounded-2xl border border-default-200 p-5">
        {/* Calendar */}
        <div className="flex min-w-0 flex-col items-start gap-4">
          <h2 className="text-lg font-semibold">۱. انتخاب تاریخ جلالی</h2>

          <I18nProvider locale={PERSIAN_LOCALE}>
            <div dir="rtl" lang="fa" className="max-w-full">
              <Calendar
                aria-label="انتخاب تاریخ رزرو"
                value={selectedDate}
                onChange={setSelectedDate}
                firstDayOfWeek="sat"
              >
                <Calendar.Header>
                  <Calendar.Heading />
                  <Calendar.NavButton slot="previous" aria-label="ماه قبل" />
                  <Calendar.NavButton slot="next" aria-label="ماه بعد" />
                </Calendar.Header>

                <Calendar.Grid>
                  <Calendar.GridHeader>
                    {(day) => <Calendar.HeaderCell>{day}</Calendar.HeaderCell>}
                  </Calendar.GridHeader>

                  <Calendar.GridBody>
                    {(date) => <Calendar.Cell date={date} />}
                  </Calendar.GridBody>
                </Calendar.Grid>
              </Calendar>
            </div>
          </I18nProvider>

          <p className="text-xs leading-5 text-default-500">
            برای آزمون دسترس‌پذیری، از کلیدهای جهت‌دار، Enter و Tab استفاده کن.
          </p>
        </div>

        {/* Time field */}
        <div className="flex min-w-0 flex-col gap-4">
          <h2 className="text-lg font-semibold">۲. انتخاب ساعت محلی تهران</h2>

          <I18nProvider locale={PERSIAN_LOCALE}>
            <div dir="rtl" lang="fa" className="w-full">
              <TimeField
                dir="ltr"
                aria-label="ساعت رزرو"
                hourCycle={24}
                shouldForceLeadingZeros
                value={time}
                onChange={setTime}
              >
                <Label>ساعت رزرو (۲۴ ساعته)</Label>

                <TimeField.Group>
                  <TimeField.Input>
                    {(segment) => <TimeField.Segment segment={segment} />}
                  </TimeField.Input>
                </TimeField.Group>
              </TimeField>
            </div>
          </I18nProvider>

          <p className="text-sm text-default-500">
            ساعت انتخاب‌شده:{" "}
            <code dir="ltr" className="font-medium">
              {time ? formatTime(time) : "—"}
            </code>
          </p>

          {/* Selected Jalali date */}
          <div className="rounded-xl bg-default-100 p-4">
            <p className="mb-1 text-sm text-default-500">
              تاریخ جلالی انتخاب‌شده
            </p>

            <p className="text-lg font-semibold">
              {selectedDate
                ? toPersianDigits(
                    `${selectedDate.year}/${String(selectedDate.month).padStart(
                      2,
                      "0",
                    )}/${String(selectedDate.day).padStart(2, "0")}`,
                  )
                : "تاریخی انتخاب نشده است"}
            </p>
          </div>

          {/* Conversion results */}
          <div className="rounded-xl border border-default-200 p-4">
            <p className="mb-1 text-sm text-default-500">تاریخ میلادی معادل</p>

            <code dir="ltr" className="block break-all text-sm">
              {result?.gregorianDate ?? "—"}
            </code>

            <p className="mb-1 mt-4 text-sm text-default-500">
              زمان UTC · ISO 8601
            </p>

            <code dir="ltr" className="block break-all text-sm">
              {result?.utcISO ?? "—"}
            </code>
          </div>

          <p className="text-xs leading-5 text-default-500">
            منطقه زمانی: <code dir="ltr">{BOOKITO_TIME_ZONE}</code>. ساعت
            انتخاب‌شده همراه تاریخ به UTC تبدیل می‌شود؛ پسوند Z به ساعت محلی
            اضافه نمی‌شود، بلکه خروجی حاصل تبدیل منطقه زمانی است.
          </p>
        </div>
      </section>
    </main>
  );
}
