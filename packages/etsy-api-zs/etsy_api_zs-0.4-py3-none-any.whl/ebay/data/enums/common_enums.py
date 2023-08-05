from model_utils import Choices

WeightUnitOfMeasureEnum = Choices(
    ("POUND", "Фунт"), ("KILOGRAM", "Килограмм"), ("OUNCE", "Унция"), ("GRAM", "Грамм"),
)

LengthUnitOfMeasureEnum = Choices(
    ("INCH", "Дюйм"), ("FEET", "Фут"), ("CENTIMETER", "Сантиметр"), ("METER", "Метр"),
)

TimeDurationUnitEnum = Choices(
    ("YEAR", "Год"),
    ("MONTH", "Месяц"),
    ("DAY", "День"),
    ("HOUR", "Час"),
    ("CALENDAR_DAY", "Календарный день"),
    ("BUSINESS_DAY", "Рабочий день"),
    ("MINUTE", "Минута"),
    ("SECOND", "Секунда"),
    ("MILLISECOND", "Миллисекунда"),
)

DayOfWeekEnum = Choices(
    ("MONDAY", "Понедельник"),
    ("TUESDAY", "Вторник"),
    ("WEDNESDAY", "Среда"),
    ("THURSDAY", "Четверг"),
    ("FRIDAY", "Пятница"),
    ("SATURDAY", "Суббота"),
    ("SUNDAY", "Воскресенье"),
)
